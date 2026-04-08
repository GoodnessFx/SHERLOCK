from typing import List, Dict, Any, Optional
import json
from langchain_anthropic import ChatAnthropic
from core.config import settings
from core.scorer import scorer
from core.logger import db_logger
import logging

logger = logging.getLogger(__name__)

class ProbabilityAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model_name="claude-3-5-sonnet-20240620",
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            temperature=0
        )

    async def score_market(self, market: Dict[str, Any], signals: List[Dict[str, Any]], memory_context: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Asks Claude to estimate the probability of YES for a given market.
        """
        if not settings.ANTHROPIC_API_KEY:
            db_logger.log_event("WARNING", "PROB", "ANTHROPIC_API_KEY not set. Skipping market scoring.")
            return None

        # Build prompt
        prompt = f"""
        Market: {market.get('question')}
        Current YES Price: {market.get('yes_price')}
        Description: {market.get('description', 'No description provided')}
        
        Available Signals:
        {json.dumps([{ 'type': s['type'], 'summary': s['summary'] } for s in signals], indent=2)}
        
        Historical Memory Context (similar past events):
        {json.dumps([{ 'text': m['text'], 'outcome': m['metadata'].get('outcome') } for m in memory_context], indent=2)}
        
        Task:
        You are an expert Bayesian reasoner. Your goal is to estimate the true probability (0.0 to 1.0) of this market resolving to YES, using the current market price as a prior and updating your belief based on the provided signals and historical context.

        Consider the Current YES Price ({market.get('yes_price')}) as your initial prior belief.
        Then, carefully analyze the 'Available Signals' (including any 'spread_analysis' signals) and 'Historical Memory Context'.
        Update your probability estimate based on the strength and relevance of this new evidence.
        Explain how each piece of evidence shifts your belief from the prior.

        Finally, provide your updated probability estimate (our_probability), a confidence score (0.0 to 1.0) in this estimate, and a detailed reasoning for your Bayesian update.
        Calculate the edge (your_probability - market_price).
        
        Return ONLY a JSON object in this format:
        {{
            "our_probability": float,
            "confidence": float,
            "reasoning": str,
            "signals_used": [str]
        }}
        """

        try:
            response = await self.llm.ainvoke(prompt)
            # Basic parsing of JSON from the response content
            # Claude 3.5 Sonnet is usually good at returning raw JSON when asked
            result = json.loads(response.content)
            
            our_prob = result.get("our_probability", 0.5)
            market_price = market.get("yes_price", 0.5)
            edge = our_prob - market_price
            
            # Minimum edge threshold check
            if abs(edge) < settings.MIN_EDGE_THRESHOLD:
                return None
                
            # Calculate Kelly fraction
            # Odds b = (1 - price) / price
            b = (1 - market_price) / market_price if market_price > 0 else 1.0
            kelly_fraction = scorer.kelly_fraction(our_prob, b)
            
            edge_obj = {
                "market_id": market.get("id"),
                "market_question": market.get("question"),
                "market_price": market_price,
                "our_probability": our_prob,
                "edge": edge,
                "kelly_fraction": kelly_fraction,
                "confidence": result.get("confidence", 0.5),
                "reasoning": result.get("reasoning", ""),
                "signals_used": result.get("signals_used", [])
            }
            
            db_logger.log_event("INFO", "EDGE", f"Found edge for {market['question'][:30]}: {edge:+.2f}")
            return edge_obj
        except Exception as e:
            logger.error(f"Error scoring market {market.get('id')}: {e}")
            return None

probability_agent = ProbabilityAgent()
