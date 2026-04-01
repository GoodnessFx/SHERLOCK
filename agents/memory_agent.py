from typing import List, Dict, Any, Optional
from core.memory import memory_db
from core.logger import db_logger
import logging

logger = logging.getLogger(__name__)

class MemoryAgent:
    def __init__(self):
        self.memory = memory_db

    def store_signal(self, signal: Dict[str, Any], outcome: Optional[str] = None):
        """
        KAIROS: embeds signal + metadata into ChromaDB.
        """
        text = signal.get("summary", "")
        metadata = {
            "source": signal.get("source"),
            "type": signal.get("type"),
            "resolved": outcome is not None,
            "outcome": outcome
        }
        
        # Add any relevant markets if available
        if "relevant_markets" in signal:
            metadata["relevant_markets"] = ",".join(signal["relevant_markets"])
            
        signal_id = self.memory.embed_and_store(text, metadata)
        db_logger.log_event("INFO", "MEM", f"Stored signal in memory: {text[:50]}...", {"id": signal_id})
        return signal_id

    def recall_similar(self, market_question: str, n: int = 5) -> List[Dict[str, Any]]:
        """
        KAIROS: returns n most semantically similar past signals with their outcomes.
        """
        results = self.memory.query_similar(market_question, n_results=n)
        db_logger.log_event("INFO", "MEM", f"Recalled {len(results)} similar memories for: {market_question[:30]}...")
        return results

    def update_outcome(self, signal_id: str, outcome: str, correct: bool):
        """
        When a market resolves, records if we were right or wrong (accuracy tracking).
        """
        success = self.memory.update_metadata(signal_id, {
            "resolved": True,
            "outcome": outcome,
            "correct": correct
        })
        if success:
            db_logger.log_event("INFO", "MEM", f"Updated outcome for signal {signal_id}: {outcome} (Correct: {correct})")
        return success

    def summarize_history(self) -> str:
        """
        Returns a text summary of performance.
        """
        return self.memory.export_summary()

memory_agent = MemoryAgent()
