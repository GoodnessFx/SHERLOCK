import pytest
import os
import shutil
import tempfile
import time
from unittest.mock import MagicMock
from core.memory import ChromaMemory

@pytest.fixture
def temp_memory():
    # Setup temporary directory for ChromaDB
    temp_dir = tempfile.mkdtemp()
    # Mock the embedding function to avoid downloads during tests
    mem = ChromaMemory(db_path=temp_dir)
    # Mocking the collection to avoid actual heavy operations during unit tests
    # but still test our wrapper logic
    mem.collection = MagicMock()
    
    # Mock return values for collection methods
    def mock_add(ids, documents, metadatas):
        mem.collection.get.return_value = {"ids": ids, "documents": documents, "metadatas": metadatas}
        return None
    
    mem.collection.add.side_effect = mock_add
    
    yield mem
    # Teardown
    try:
        time.sleep(1)
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Cleanup failed for {temp_dir}: {e}")

def test_store_and_recall(temp_memory):
    text = "Bitcoin will reach $100k in 2024"
    metadata = {"market_id": "btc-100k", "category": "crypto"}
    
    # Setup mock query result
    temp_memory.collection.query.return_value = {
        "ids": [["1"]],
        "documents": [[text]],
        "metadatas": [[metadata]],
        "distances": [[0.1]]
    }
    
    id = temp_memory.embed_and_store(text, metadata)
    assert id is not None
    
    results = temp_memory.query_similar("Bitcoin price prediction")
    assert len(results) > 0
    assert results[0]["text"] == text
    assert results[0]["metadata"]["market_id"] == "btc-100k"

def test_semantic_similarity_ordering(temp_memory):
    # Setup mock query results for specific queries
    def mock_query(query_texts, n_results):
        if "ETH" in query_texts[0]:
            return {
                "ids": [["1", "2"]],
                "documents": [["Ethereum price is up 5%", "The weather in London is rainy"]],
                "metadatas": [[{"cat": "crypto"}, {"cat": "weather"}]],
                "distances": [[0.1, 0.8]]
            }
        else:
            return {
                "ids": [["2", "1"]],
                "documents": [["The weather in London is rainy", "Ethereum price is up 5%"]],
                "metadatas": [[{"cat": "weather"}, {"cat": "crypto"}]],
                "distances": [[0.1, 0.8]]
            }
    
    temp_memory.collection.query.side_effect = mock_query
    
    # Query for crypto should return crypto first
    results = temp_memory.query_similar("ETH and BTC prices")
    assert results[0]["metadata"]["cat"] == "crypto"
    
    # Query for rain should return weather first
    results = temp_memory.query_similar("Will it rain in London?")
    assert results[0]["metadata"]["cat"] == "weather"

def test_accuracy_stats_calculation(temp_memory):
    # Mock get() to return fixed records
    temp_memory.collection.get.return_value = {
        "ids": ["1", "2", "3"],
        "documents": ["M1", "M2", "M3"],
        "metadatas": [
            {"resolved": True, "correct": True},
            {"resolved": True, "correct": False},
            {"resolved": False}
        ]
    }
    
    stats = temp_memory.get_accuracy_stats()
    assert stats["total_predictions"] == 2
    assert stats["correct"] == 1
    assert stats["accuracy_pct"] == 50.0

def test_outcome_update(temp_memory):
    # Mock get() for update_metadata
    temp_memory.collection.get.return_value = {
        "ids": ["1"],
        "metadatas": [{"resolved": False}]
    }
    
    id = "1"
    success = temp_memory.update_metadata(id, {"resolved": True, "correct": True, "outcome": "YES"})
    assert success is True
    assert temp_memory.collection.update.called
