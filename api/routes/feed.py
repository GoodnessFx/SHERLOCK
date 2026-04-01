from fastapi import APIRouter
from core.logger import db_logger
from datetime import datetime

router = APIRouter()

@router.get("/feed")
async def get_feed(limit: int = 50):
    """
    Returns the last 50 log events for the initial frontend load.
    """
    logs = db_logger.get_recent_logs(limit=limit)
    return {
        "data": logs,
        "timestamp": datetime.now().isoformat(),
        "count": len(logs)
    }
