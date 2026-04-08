from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from core.polymarket import polymarket
from core.logger import db_logger
from agents.research_agent import research_agent
from agents.memory_agent import memory_agent
from agents.probability_agent import probability_agent
from agents.execution_agent import execution_agent
import asyncio
import uuid
import datetime
import logging

logger = logging.getLogger(__name__)

# State schema for the orchestrator
class AgentState(TypedDict):
    run_id: str
    markets: List[Dict[str, Any]]
    signals: List[Dict[str, Any]] # Global signals
    market_signals: Dict[str, List[Dict[str, Any]]] # market_id -> list of market-specific signals
    memory_context: Dict[str, List[Dict[str, Any]]]  # market_id -> list of memories
    edges: List[Dict[str, Any]]
    execution_plan: List[Dict[str, Any]]
    log: List[str]
    errors: List[str]

async def fetch_markets_node(state: AgentState) -> AgentState:
    db_logger.log_event("INFO", "RUN", f"Run {state['run_id']} started. Fetching markets...")
    try:
        markets = await polymarket.get_markets(limit=20, active=True)
        if not markets:
            state["errors"].append("No active markets returned from Polymarket.")
            return state
        state["markets"] = markets
        db_logger.log_event("INFO", "RUN", f"Fetched {len(markets)} active markets.")
    except Exception as e:
        state["errors"].append(f"Error fetching markets: {e}")
    return state

async def fetch_signals_node(state: AgentState) -> AgentState:
    db_logger.log_event("INFO", "RUN", "Fetching external signals...")
    try:
        market_questions = [market.get("question", "") for market in state["markets"]]
        signals = await research_agent.fetch_all_signals(market_questions)
        state["signals"] = signals
        db_logger.log_event("INFO", "RUN", f"Fetched {len(signals)} external signals.")
    except Exception as e:
        state["errors"].append(f"Error fetching signals: {e}")
    return state

async def fetch_market_signals_node(state: AgentState) -> AgentState:
    db_logger.log_event("INFO", "RUN", "Fetching market-specific signals (Volatility/On-chain)...")
    try:
        market_signals = {}
        tasks = []
        for market in state["markets"]:
            tasks.append(research_agent.fetch_market_specific_signals(market["id"]))
        
        results = await asyncio.gather(*tasks)
        for i, market in enumerate(state["markets"]):
            market_signals[market["id"]] = results[i]
        state["market_signals"] = market_signals
    except Exception as e:
        state["errors"].append(f"Error fetching market signals: {e}")
    return state

async def recall_memory_node(state: AgentState) -> AgentState:
    db_logger.log_event("INFO", "RUN", "Recalling past similar conditions from memory...")
    try:
        memory_context = {}
        for market in state["markets"]:
            memories = memory_agent.recall_similar(market["question"], n=5)
            memory_context[market["id"]] = memories
        state["memory_context"] = memory_context
    except Exception as e:
        state["errors"].append(f"Error recalling memory: {e}")
    return state

async def score_edges_node(state: AgentState) -> AgentState:
    db_logger.log_event("INFO", "RUN", "Scoring markets for potential edges...")
    try:
        edges = []
        # Score each market in parallel if possible, but limit concurrency for LLM API
        tasks = []
        for market in state["markets"]:
            market_id = market["id"]
            memories = state["memory_context"].get(market_id, [])
            # Combine global signals with market-specific signals
            all_market_signals = state["signals"] + state.get("market_signals", {}).get(market_id, [])
            tasks.append(probability_agent.score_market(market, all_market_signals, memories))
        
        results = await asyncio.gather(*tasks)
        edges = [e for e in results if e is not None]
        state["edges"] = edges
        db_logger.log_event("INFO", "RUN", f"Found {len(edges)} edges with significant confidence.")
    except Exception as e:
        state["errors"].append(f"Error scoring edges: {e}")
    return state

async def plan_execution_node(state: AgentState) -> AgentState:
    db_logger.log_event("INFO", "RUN", "Generating execution recommendations...")
    try:
        recommendations = execution_agent.format_recommendations(state["edges"])
        state["execution_plan"] = recommendations
    except Exception as e:
        state["errors"].append(f"Error planning execution: {e}")
    return state

async def store_memory_node(state: AgentState) -> AgentState:
    db_logger.log_event("INFO", "RUN", "Persisting run findings to long-term memory...")
    try:
        for edge in state["edges"]:
            # Create a signal object to store the edge finding
            signal = {
                "source": "SherlockOrchestrator",
                "type": "prediction",
                "summary": f"Predicted {edge['our_probability']:.2f} for {edge['market_question']}. Market price: {edge['market_price']:.2f}.",
                "confidence": edge["confidence"],
                "relevant_markets": [edge["market_id"]]
            }
            memory_agent.store_signal(signal)
            db_logger.store_edge(edge, state["run_id"])
    except Exception as e:
        state["errors"].append(f"Error storing memory: {e}")
    return state

async def broadcast_node(state: AgentState) -> AgentState:
    db_logger.log_event("INFO", "RUN", f"Run {state['run_id']} complete.")
    # In a real app, this would push to WebSockets.
    # Our API layer will handle the WebSocket broadcast when it detects new log entries.
    return state

def should_continue(state: AgentState) -> str:
    if state["errors"] and not state["markets"]:
        return "end"
    if not state["markets"]:
        return "end"
    return "continue"

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("fetch_markets", fetch_markets_node)
workflow.add_node("fetch_signals", fetch_signals_node)
workflow.add_node("fetch_market_signals", fetch_market_signals_node)
workflow.add_node("recall_memory", recall_memory_node)
workflow.add_node("score_edges", score_edges_node)
workflow.add_node("plan_execution", plan_execution_node)
workflow.add_node("store_memory", store_memory_node)
workflow.add_node("broadcast", broadcast_node)

# Set entry point
workflow.set_entry_point("fetch_markets")

# Add edges
workflow.add_edge("fetch_markets", "fetch_signals")
workflow.add_edge("fetch_signals", "fetch_market_signals")
workflow.add_edge("fetch_market_signals", "recall_memory")
workflow.add_edge("recall_memory", "score_edges")
workflow.add_edge("score_edges", "plan_execution")
workflow.add_edge("plan_execution", "store_memory")
workflow.add_edge("store_memory", "broadcast")
workflow.add_edge("broadcast", END)

# Compile the graph
orchestrator_graph = workflow.compile()

async def run_orchestrator():
    run_id = str(uuid.uuid4())[:8]
    initial_state: AgentState = {
        "run_id": run_id,
        "markets": [],
        "signals": [],
        "market_signals": {},
        "memory_context": {},
        "edges": [],
        "execution_plan": [],
        "log": [],
        "errors": []
    }
    
    try:
        final_state = await orchestrator_graph.ainvoke(initial_state)
        return final_state
    except Exception as e:
        db_logger.log_event("ERROR", "RUN", f"Fatal error in orchestrator: {e}")
        return initial_state
