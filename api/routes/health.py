from fastapi import APIRouter
from core.logger import db_logger
from core.memory import memory_db
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Returns API health status, last run, and memory stats.
    """
    recent_runs = db_logger.get_recent_logs(limit=10)
    last_run = next((log for log in recent_runs if log["type"] == "DAEMON" and "completed" in log["message"]), None)
    
    stats = memory_db.get_accuracy_stats()
    
    return {
        "status": "healthy",
        "last_run": last_run["timestamp"] if last_run else None,
        "run_count": stats.get("total_predictions", 0),
        "memory_size": stats.get("total_predictions", 0),
        "timestamp": datetime.now().isoformat()
    }
