from fastapi import APIRouter
from core.logger import db_logger
from core.memory import memory_db
from core.scorer import scorer
from datetime import datetime
import json

router = APIRouter()

@router.get("/track-record")
async def get_track_record():
    """
    Returns the current track record including accuracy and P&L simulation.
    """
    stats = memory_db.get_accuracy_stats()
    edges = db_logger.get_latest_edges(limit=100)
    
    # Simulate P&L from the latest 100 edges
    pnl_sim = scorer.simulate_pnl(edges, bankroll=1000)
    
    return {
        "data": {
            "total_predictions": stats["total_predictions"],
            "correct": stats["correct"],
            "accuracy_pct": stats["accuracy_pct"],
            "avg_edge": sum(abs(e["edge"]) for e in edges) / len(edges) if edges else 0,
            "pnl_simulation": pnl_sim
        },
        "timestamp": datetime.now().isoformat()
    }
