import httpx
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PolymarketClient:
    BASE_URL = "https://clob.polymarket.com"

    def __init__(self):
        self.client = httpx.AsyncClient(base_url=self.BASE_URL, timeout=30.0)

    async def get_markets(self, limit: int = 20, active: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch active markets sorted by volume.
        """
        try:
            # Polymarket CLOB API: GET /sampling-markets
            # This is a common endpoint for active markets.
            # Alternatively, use /markets for specific details.
            params = {
                "active": "true" if active else "false",
                "limit": limit,
                "order": "volume_24h",
                "ascending": "false"
            }
            response = await self.client.get("/sampling-markets", params=params)
            response.raise_for_status()
            markets_raw = response.json()
            
            processed_markets = []
            for m in markets_raw:
                # Extract relevant fields
                # Note: Polymarket API structure might vary slightly, but this is the general schema
                processed_markets.append({
                    "id": m.get("condition_id"),
                    "question": m.get("question"),
                    "description": m.get("description", ""),
                    "end_date": m.get("end_date_iso"),
                    "yes_price": m.get("tokens", [{}])[0].get("price", 0.5),
                    "no_price": m.get("tokens", [{}])[1].get("price", 0.5) if len(m.get("tokens", [])) > 1 else 0.5,
                    "volume_24h": float(m.get("volume_24h", 0)),
                    "total_volume": float(m.get("volume", 0)),
                    "category": m.get("category", "General"),
                    "tags": m.get("tags", [])
                })
            return processed_markets
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []

    async def get_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch single market details.
        """
        try:
            response = await self.client.get(f"/markets/{market_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            return None

    async def get_recent_trades(self, market_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Fetch recent trades for a specific market.
        """
        try:
            # GET /trades-by-market-id
            params = {"condition_id": market_id, "limit": limit}
            response = await self.client.get("/trades-by-market-id", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching trades for market {market_id}: {e}")
            return []

    async def detect_volume_spike(self, market_id: str) -> float:
        """
        Detect if current volume is spiking compared to average.
        Returns spike_ratio (>2.0 = unusual).
        """
        try:
            # Simple implementation: compare 24h volume to total volume or historical average if available
            # For now, we'll return a placeholder spike detection logic
            market = await self.get_market(market_id)
            if not market:
                return 1.0
            
            volume_24h = float(market.get("volume_24h", 0))
            total_volume = float(market.get("volume", 0))
            
            # If 24h volume is more than 20% of total volume, consider it a spike
            if total_volume > 0:
                spike_ratio = (volume_24h / (total_volume / 7)) if total_volume > 0 else 1.0
                return spike_ratio
            return 1.0
        except Exception as e:
            logger.error(f"Error detecting volume spike: {e}")
            return 1.0

    async def close(self):
        await self.client.aclose()

polymarket = PolymarketClient()
