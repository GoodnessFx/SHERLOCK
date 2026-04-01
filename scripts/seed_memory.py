import asyncio
import uuid
from core.memory import memory_db
from core.logger import db_logger

async def seed():
    print("Seeding SHERLOCK memory with historical data...")
    
    historical_signals = [
        {
            "text": "Bitcoin price crossed $70k after SEC approval of spot ETFs.",
            "metadata": {
                "market_id": "btc-spot-etf",
                "market_question": "Will BTC cross $70k by end of Q1?",
                "our_probability": 0.85,
                "market_price_at_time": 0.65,
                "edge": 0.2,
                "resolved": True,
                "correct": True,
                "outcome": "YES",
                "type": "crypto"
            }
        },
        {
            "text": "Major hurricane predicted for Florida coast in late August.",
            "metadata": {
                "market_id": "hurricane-fl-2024",
                "market_question": "Will a major hurricane hit FL in Aug 2024?",
                "our_probability": 0.7,
                "market_price_at_time": 0.4,
                "edge": 0.3,
                "resolved": True,
                "correct": True,
                "outcome": "YES",
                "type": "weather"
            }
        },
        {
            "text": "US Election: Polling data shows narrowing lead in key swing states.",
            "metadata": {
                "market_id": "us-election-2024",
                "market_question": "Will candidate X win swing state Y?",
                "our_probability": 0.45,
                "market_price_at_time": 0.55,
                "edge": -0.1,
                "resolved": True,
                "correct": False,
                "outcome": "YES",
                "type": "news"
            }
        }
    ]
    
    for signal in historical_signals:
        memory_db.embed_and_store(signal["text"], signal["metadata"])
        print(f"Stored: {signal['text'][:50]}...")

    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed())
