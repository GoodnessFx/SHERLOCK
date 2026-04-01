from typing import List, Dict, Any, Optional
from core.logger import db_logger
import logging

logger = logging.getLogger(__name__)

class ExecutionAgent:
    """
    Formats scored edges into trade recommendations. 
    Does NOT auto-execute.
    """
    def format_recommendations(self, edges_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        db_logger.log_event("INFO", "EXEC", f"Processing {len(edges_list)} edges for recommendations...")
        
        recommendations = []
        for edge in edges_list:
            # Check for PRIORITY (edge > 0.15 and confidence > 0.7)
            is_priority = (abs(edge.get("edge", 0)) > 0.15) and (edge.get("confidence", 0) > 0.7)
            
            recommendation = {
                "market_id": edge.get("market_id"),
                "market_question": edge.get("market_question"),
                "action": "BUY YES" if edge.get("edge", 0) > 0 else "BUY NO",
                "our_probability": edge.get("our_probability"),
                "market_price": edge.get("market_price"),
                "edge_size": f"{edge.get('edge', 0):+.2%}",
                "kelly_fraction": f"{edge.get('kelly_fraction', 0):.2%}",
                "confidence": edge.get("confidence"),
                "reasoning": edge.get("reasoning"),
                "signals": edge.get("signals_used", []),
                "priority": is_priority
            }
            
            recommendations.append(recommendation)
            if is_priority:
                db_logger.log_event("WARNING", "EXEC", f"PRIORITY EDGE FOUND: {recommendation['market_question'][:30]}...")

        # Sort recommendations: priorities first, then by absolute edge size
        return sorted(recommendations, key=lambda x: (x["priority"], abs(float(x["edge_size"].replace('%', '')))), reverse=True)

execution_agent = ExecutionAgent()
