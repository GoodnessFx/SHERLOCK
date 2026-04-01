import chromadb
import uuid
import datetime
from typing import List, Dict, Any, Optional
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class ChromaMemory:
    def __init__(self, db_path: str = settings.CHROMA_DB_PATH):
        self.db_path = db_path
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(name="oracle_memory")

    def embed_and_store(self, text: str, metadata: Dict[str, Any]):
        """
        Store a text signal and metadata into ChromaDB.
        """
        try:
            id = str(uuid.uuid4())
            metadata["timestamp"] = datetime.datetime.now().isoformat()
            self.collection.add(
                ids=[id],
                documents=[text],
                metadatas=[metadata]
            )
            return id
        except Exception as e:
            logger.error(f"Error storing signal in memory: {e}")
            return None

    def query_similar(self, text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a semantic search in memory.
        """
        try:
            results = self.collection.query(
                query_texts=[text],
                n_results=n_results
            )
            
            # Reformat results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else 0
                    })
            return formatted_results
        except Exception as e:
            logger.error(f"Error querying memory: {e}")
            return []

    def get_recent(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Retrieve recent memories within the last X days.
        Note: ChromaDB filtering can be complex; a simpler way is to filter after retrieval if the dataset is small.
        """
        try:
            # For small-scale local vector store, we can just get all and filter
            all_memories = self.collection.get()
            recent_memories = []
            now = datetime.datetime.now()
            
            if all_memories["ids"]:
                for i in range(len(all_memories["ids"])):
                    metadata = all_memories["metadatas"][i]
                    timestamp_str = metadata.get("timestamp")
                    if timestamp_str:
                        timestamp = datetime.datetime.fromisoformat(timestamp_str)
                        if (now - timestamp).days <= days:
                            recent_memories.append({
                                "id": all_memories["ids"][i],
                                "text": all_memories["documents"][i],
                                "metadata": metadata
                            })
            return recent_memories
        except Exception as e:
            logger.error(f"Error fetching recent memories: {e}")
            return []

    def update_metadata(self, id: str, updates: Dict[str, Any]):
        """
        Update metadata for a specific record (e.g., when a market resolves).
        """
        try:
            # First, fetch existing metadata
            existing = self.collection.get(ids=[id])
            if not existing["ids"]:
                return False
            
            new_metadata = existing["metadatas"][0]
            new_metadata.update(updates)
            
            self.collection.update(
                ids=[id],
                metadatas=[new_metadata]
            )
            return True
        except Exception as e:
            logger.error(f"Error updating memory metadata: {e}")
            return False

    def get_accuracy_stats(self) -> Dict[str, Any]:
        """
        Compute overall accuracy from resolved predictions.
        """
        try:
            all_memories = self.collection.get()
            total_predictions = 0
            correct_predictions = 0
            
            if all_memories["ids"]:
                for metadata in all_memories["metadatas"]:
                    if metadata.get("resolved") is True:
                        total_predictions += 1
                        if metadata.get("correct") is True:
                            correct_predictions += 1
            
            accuracy_pct = (correct_predictions / total_predictions * 100) if total_predictions > 0 else 0
            return {
                "total_predictions": total_predictions,
                "correct": correct_predictions,
                "accuracy_pct": accuracy_pct
            }
        except Exception as e:
            logger.error(f"Error calculating accuracy stats: {e}")
            return {"total_predictions": 0, "correct": 0, "accuracy_pct": 0}

    def export_summary(self) -> str:
        """
        Return a markdown-formatted summary of recent performance.
        """
        stats = self.get_accuracy_stats()
        summary = f"### Recent Performance Summary\n"
        summary += f"- **Total Predictions:** {stats['total_predictions']}\n"
        summary += f"- **Accuracy:** {stats['accuracy_pct']:.1f}%\n"
        summary += f"- **Correct Calls:** {stats['correct']}\n"
        
        # Add a note about the latest 3 resolved markets if available
        # This is a placeholder for more detailed logic
        return summary

memory_db = ChromaMemory()
