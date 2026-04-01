import httpx
import asyncio
import logging
from typing import List, Dict, Any, Optional
from core.config import settings

logger = logging.getLogger(__name__)

class SignalFetcher:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)

    async def fetch_weather(self, city: str = "London") -> Dict[str, Any]:
        """
        Fetch current weather data using OpenWeatherMap.
        """
        try:
            if not settings.OPENWEATHER_API_KEY:
                return {"source": "OpenWeatherMap", "type": "weather", "summary": "No API key provided", "confidence": 0.0, "relevant_markets": [], "raw": {}}
            
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.OPENWEATHER_API_KEY}&units=metric"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            temp = data.get("main", {}).get("temp")
            weather_desc = data.get("weather", [{}])[0].get("description", "unknown")
            
            summary = f"Weather in {city}: {temp}°C, {weather_desc}"
            return {
                "source": "OpenWeatherMap",
                "type": "weather",
                "summary": summary,
                "confidence": 0.9,
                "relevant_markets": ["weather", "temperature", city.lower()],
                "raw": data
            }
        except Exception as e:
            logger.error(f"Error fetching weather: {e}")
            return {"source": "OpenWeatherMap", "type": "weather", "summary": f"Error fetching weather: {e}", "confidence": 0.0, "relevant_markets": [], "raw": {}}

    async def fetch_crypto_prices(self, ids: str = "bitcoin,ethereum,solana") -> Dict[str, Any]:
        """
        Fetch current crypto prices using CoinGecko.
        """
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true"
            # Optional: Add API key if available
            headers = {}
            if settings.COINGECKO_API_KEY:
                headers["x-cg-demo-api-key"] = settings.COINGECKO_API_KEY
                
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            summary_parts = []
            for coin, info in data.items():
                price = info.get("usd")
                change = info.get("usd_24h_change", 0)
                summary_parts.append(f"{coin.capitalize()}: ${price:,.2f} ({change:+.2f}%)")
            
            summary = "Crypto Prices: " + " | ".join(summary_parts)
            return {
                "source": "CoinGecko",
                "type": "crypto",
                "summary": summary,
                "confidence": 0.95,
                "relevant_markets": ["crypto", "bitcoin", "ethereum", "solana"],
                "raw": data
            }
        except Exception as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return {"source": "CoinGecko", "type": "crypto", "summary": f"Error fetching crypto prices: {e}", "confidence": 0.0, "relevant_markets": [], "raw": {}}

    async def fetch_news_headlines(self) -> Dict[str, Any]:
        """
        Fetch recent news headlines using NewsAPI.
        """
        try:
            if not settings.NEWS_API_KEY:
                return {"source": "NewsAPI", "type": "news", "summary": "No API key provided", "confidence": 0.0, "relevant_markets": [], "raw": {}}
            
            url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=10&apiKey={settings.NEWS_API_KEY}"
            response = await self.client.get(url)
            response.raise_for_status()
            data = response.json()
            
            articles = data.get("articles", [])
            headlines = [a.get("title") for a in articles if a.get("title")]
            summary = "Top Headlines: " + " | ".join(headlines[:5])
            
            return {
                "source": "NewsAPI",
                "type": "news",
                "summary": summary,
                "confidence": 0.8,
                "relevant_markets": ["news", "politics", "world"],
                "raw": data
            }
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return {"source": "NewsAPI", "type": "news", "summary": f"Error fetching news: {e}", "confidence": 0.0, "relevant_markets": [], "raw": {}}

    async def close(self):
        await self.client.aclose()

signal_fetcher = SignalFetcher()
