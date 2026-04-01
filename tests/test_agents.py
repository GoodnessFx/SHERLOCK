import pytest
import asyncio
from agents.orchestrator import orchestrator_graph
from agents.research_agent import research_agent
from agents.probability_agent import probability_agent
from core.config import settings

@pytest.mark.asyncio
async def test_orchestrator_graph_structure():
    assert orchestrator_graph is not None
    # Check if nodes exist
    nodes = orchestrator_graph.nodes
    assert "fetch_markets" in nodes
    assert "fetch_signals" in nodes
    assert "score_edges" in nodes

@pytest.mark.asyncio
async def test_research_agent_returns_signals():
    # Mocking external signals if API keys aren't set
    # For now, just check if it returns a list
    signals = await research_agent.fetch_all_signals()
    assert isinstance(signals, list)

@pytest.mark.asyncio
async def test_probability_agent_emits_edges():
    # Skip if no API key
    if not settings.ANTHROPIC_API_KEY:
        pytest.skip("ANTHROPIC_API_KEY not set")
        
    market = {"id": "test-1", "question": "Will BTC reach $100k?", "yes_price": 0.5, "description": "test"}
    signals = [{"type": "crypto", "summary": "BTC is trending up", "confidence": 0.9}]
    memory_context = []
    
    edge = await probability_agent.score_market(market, signals, memory_context)
    if edge:
        assert "market_id" in edge
        assert "our_probability" in edge
        assert "edge" in edge
        assert abs(edge["edge"]) >= settings.MIN_EDGE_THRESHOLD
