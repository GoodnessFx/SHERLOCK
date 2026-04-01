from typing import List, Dict, Any, Optional
from core.signals import signal_fetcher
from core.polymarket import polymarket
from core.logger import db_logger
import asyncio
import logging

logger = logging.getLogger(__name__)

class ResearchAgent:
    """
    Fetches and returns structured signal data from weather, crypto, news, and on-chain.
    """
    async def fetch_all_signals(self) -> List[Dict[str, Any]]:
        db_logger.log_event("INFO", "SIG", "Starting research agent run...")
        
        # Fetch signals in parallel
        tasks = [
            signal_fetcher.fetch_weather("London"),  # Defaulting to London for weather
            signal_fetcher.fetch_crypto_prices(),
            signal_fetcher.fetch_news_headlines()
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Flatten and filter out failed fetches
        signals = [s for s in results if s.get("confidence", 0) > 0]
        
        db_logger.log_event("INFO", "SIG", f"Research complete. Found {len(signals)} signals.")
        return signals

    async def fetch_onchain_signals(self, market_id: str) -> Dict[str, Any]:
        """
        Fetch Polymarket-specific on-chain/trade signals (detect sharp money / unusual volume).
        """
        try:
            trades = await polymarket.get_recent_trades(market_id, limit=50)
            spike_ratio = await polymarket.detect_volume_spike(market_id)
            
            summary = f"On-chain analysis for market {market_id[:10]}: Spike ratio {spike_ratio:.2f}."
            if spike_ratio > 2.0:
                summary += " UNUSUAL VOLUME DETECTED."
                
            return {
                "source": "Polymarket",
                "type": "onchain",
                "summary": summary,
                "confidence": 0.85,
                "relevant_markets": [market_id],
                "raw": {"trades": trades, "spike_ratio": spike_ratio}
            }
        except Exception as e:
            logger.error(f"Error fetching on-chain signals for {market_id}: {e}")
            return {"source": "Polymarket", "type": "onchain", "summary": f"Error: {e}", "confidence": 0.0, "relevant_markets": [], "raw": {}}

research_agent = ResearchAgent()
