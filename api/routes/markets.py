from fastapi import APIRouter
from core.polymarket import polymarket
from core.logger import db_logger
from datetime import datetime
import asyncio

router = APIRouter()

@router.get("/markets")
async def get_monitored_markets():
    """
    Returns the list of active markets currently being monitored.
    """
    try:
        markets = await polymarket.get_markets(limit=20, active=True)
        # Add volume spike info for each market
        enriched_markets = []
        for m in markets:
            spike_ratio = await polymarket.detect_volume_spike(m["id"])
            m["spike_ratio"] = spike_ratio
            enriched_markets.append(m)
            
        return {
            "data": enriched_markets,
            "timestamp": datetime.now().isoformat(),
            "count": len(enriched_markets)
        }
    except Exception as e:
        return {
            "data": [],
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
