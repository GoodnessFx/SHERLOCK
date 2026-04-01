import sqlite3
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.config import settings
import os

# Ensure data directory exists
os.makedirs(os.path.dirname(settings.SQLITE_DB_PATH), exist_ok=True)

# Standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agent.log")
    ]
)

logger = logging.getLogger("SHERLOCK")

class DatabaseLogger:
    def __init__(self, db_path: str = settings.SQLITE_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Logs table for live feed
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    level TEXT,
                    type TEXT,
                    message TEXT,
                    payload TEXT
                )
            """)
            
            # Edges table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id TEXT PRIMARY KEY,
                    market_id TEXT,
                    market_question TEXT,
                    market_price REAL,
                    our_probability REAL,
                    edge REAL,
                    kelly_fraction REAL,
                    confidence REAL,
                    reasoning TEXT,
                    signals_used TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    run_id TEXT
                )
            """)
            
            # Track record table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS track_record (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    market_id TEXT,
                    market_question TEXT,
                    prediction REAL,
                    actual_outcome TEXT,
                    correct BOOLEAN,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Run stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS run_stats (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    markets_processed INTEGER,
                    edges_found INTEGER,
                    status TEXT
                )
            """)
            
            conn.commit()

    def log_event(self, level: str, event_type: str, message: str, payload: Optional[Dict[str, Any]] = None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs (level, type, message, payload) VALUES (?, ?, ?, ?)",
                (level, event_type, message, json.dumps(payload) if payload else None)
            )
            conn.commit()
        
        # Also log to standard logger
        log_msg = f"[{event_type}] {message}"
        if level == "INFO":
            logger.info(log_msg)
        elif level == "WARNING":
            logger.warning(log_msg)
        elif level == "ERROR":
            logger.error(log_msg)

    def store_edge(self, edge: Dict[str, Any], run_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO edges 
                (id, market_id, market_question, market_price, our_probability, edge, kelly_fraction, confidence, reasoning, signals_used, run_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"{edge['market_id']}_{run_id}",
                edge['market_id'],
                edge['market_question'],
                edge['market_price'],
                edge['our_probability'],
                edge['edge'],
                edge['kelly_fraction'],
                edge['confidence'],
                edge['reasoning'],
                json.dumps(edge['signals_used']),
                run_id
            ))
            conn.commit()

    def get_recent_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_latest_edges(self, limit: int = 20) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM edges ORDER BY timestamp DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

db_logger = DatabaseLogger()
