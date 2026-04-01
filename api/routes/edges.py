from fastapi import APIRouter
from core.logger import db_logger
from datetime import datetime

router = APIRouter()

@router.get("/edges")
async def get_edges():
    edges = db_logger.get_latest_edges(limit=20)
    return {
        "data": edges,
        "timestamp": datetime.now().isoformat(),
        "count": len(edges)
    }
