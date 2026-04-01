import asyncio
import pandas as pd
from core.memory import memory_db
from core.scorer import Scorer
from core.logger import db_logger

async def run_backtest():
    print("Running SHRLOCK Backtest on historical memory data...")
    
    # Get all memories from ChromaDB
    all_memories = memory_db.collection.get()
    
    if not all_memories["ids"]:
        print("No historical data found in memory. Please run 'make seed' first.")
        return

    results = []
    for i in range(len(all_memories["ids"])):
        metadata = all_memories["metadatas"][i]
        if metadata.get("resolved") is True:
            results.append({
                "question": metadata.get("market_question", "Unknown"),
                "our_prob": metadata.get("our_probability", 0.5),
                "market_price": metadata.get("market_price_at_time", 0.5),
                "edge": metadata.get("edge", 0),
                "correct": metadata.get("correct", False),
                "type": metadata.get("type", "general")
            })
    
    if not results:
        print("No resolved predictions found for backtesting.")
        return

    df = pd.DataFrame(results)
    
    accuracy = df["correct"].mean() * 100
    avg_edge = df["edge"].abs().mean() * 100
    
    print("\n--- BACKTEST RESULTS ---")
    print(f"Total Samples: {len(df)}")
    print(f"Overall Accuracy: {accuracy:.1f}%")
    print(f"Average Absolute Edge: {avg_edge:.1f}%")
    
    print("\nAccuracy by Type:")
    print(df.groupby("type")["correct"].mean() * 100)
    
    # Simulate P&L
    pnl_sim = Scorer.simulate_pnl(results, bankroll=1000)
    print("\n--- P&L SIMULATION ---")
    print(f"Expected Value: ${pnl_sim['expected_value']:.2f}")
    print(f"Sharpe Ratio: {pnl_sim['sharpe_ratio']:.2f}")

if __name__ == "__main__":
    asyncio.run(run_backtest())
