import pytest
import httpx
from core.polymarket import PolymarketClient

@pytest.mark.asyncio
async def test_get_markets_returns_list():
    client = PolymarketClient()
    markets = await client.get_markets(limit=5)
    assert isinstance(markets, list)
    if markets:
        assert "id" in markets[0]
        assert "question" in markets[0]
    await client.close()

@pytest.mark.asyncio
async def test_market_schema_valid():
    client = PolymarketClient()
    markets = await client.get_markets(limit=1)
    if markets:
        m = markets[0]
        required_keys = ["id", "question", "yes_price", "no_price", "volume_24h"]
        for key in required_keys:
            assert key in m
    await client.close()

@pytest.mark.asyncio
async def test_volume_spike_detection():
    client = PolymarketClient()
    # Mock or real test
    spike = await client.detect_volume_spike("non-existent-id")
    assert isinstance(spike, float)
    assert spike >= 0.0
    await client.close()

@pytest.mark.asyncio
async def test_handles_api_error_gracefully():
    client = PolymarketClient()
    # Force an error by using a bad base URL or similar
    client.BASE_URL = "https://invalid-url-sherlock.com"
    markets = await client.get_markets()
    assert markets == []
    await client.close()
