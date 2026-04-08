import httpx
import asyncio
import logging
from typing import List, Dict, Any, Optional
from core.config import settings
from core.polymarket import polymarket

logger = logging.getLogger(__name__)

class SignalFetcher:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=15.0)

    async def fetch_polymarket_spread_data(self, market_question_keywords: List[str]) -> Dict[str, Any]:
        """
        Fetches Polymarket data for markets related to the given keywords and performs spread analysis.
        This is a placeholder for a more sophisticated spread analysis.
        """
        try:
            # For now, we'll just fetch a few markets based on keywords
            # A real implementation would need to identify truly "related" markets
            # e.g., "BTC price at 5 PM" and "BTC price at 5:15 PM"
            
            # This is a simplified example. In a real scenario, you'd need to:
            # 1. Identify truly related markets (e.g., same underlying asset, different expiry/strike)
            # 2. Fetch their prices
            # 3. Calculate the spread
            # 4. Analyze the deviation from historical spread
            
            # Example: Fetch markets that contain any of the keywords
            all_markets = await polymarket.get_markets(limit=50, active=True)
            related_markets = [
                m for m in all_markets 
                if any(keyword.lower() in m.get('question', '').lower() for keyword in market_question_keywords)
            ]

            if len(related_markets) < 2:
                return {
                    "source": "PolymarketSpread",
                    "type": "spread_analysis",
                    "summary": f"Not enough related markets found for keywords: {', '.join(market_question_keywords)}",
                    "confidence": 0.0,
                    "relevant_markets": [],
                    "raw": {}
                }

            # Simple spread calculation (e.g., between the first two related markets found)
            # This needs to be much more robust for actual trading
            market1 = related_markets[0]
            market2 = related_markets[1]

            price1 = market1.get('yes_price', 0)
            price2 = market2.get('yes_price', 0)
            
            spread = abs(price1 - price2)
            
            summary = (f"Spread analysis for markets related to '{', '.join(market_question_keywords)}': "
                       f"Market 1 ({market1.get('question')}) price: {price1}, "
                       f"Market 2 ({market2.get('question')}) price: {price2}, "
                       f"Calculated Spread: {spread:.4f}")

            return {
                "source": "PolymarketSpread",
                "type": "spread_analysis",
                "summary": summary,
                "confidence": 0.7, # Placeholder confidence
                "relevant_markets": [m['id'] for m in related_markets],
                "raw": {"related_markets": related_markets, "spread": spread}
            }

        except Exception as e:
            logger.error(f"Error fetching Polymarket spread data: {e}")
            return {"source": "PolymarketSpread", "type": "spread_analysis", "summary": f"Error: {e}", "confidence": 0.0, "relevant_markets": [], "raw": {}}

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

    async def fetch_social_sentiment(self, keywords: List[str]) -> Dict[str, Any]:
        """
        Layer 5: Sentiment AI. Scans social media/news for real-time sentiment shifts.
        Placeholder for a real Twitter/X or specialized news sentiment API.
        """
        try:
            # In a real scenario, this would call Twitter/X API or a sentiment analysis service
            # For now, we simulate a sentiment score based on the presence of keywords in news
            news_data = await self.fetch_news_headlines()
            headlines = news_data.get("summary", "")
            
            sentiment_score = 0.5 # Neutral
            hits = 0
            for kw in keywords:
                if kw.lower() in headlines.lower():
                    hits += 1
            
            if hits > 0:
                sentiment_score = 0.5 + (hits * 0.1) # Simple positive bias for keyword hits
                sentiment_score = min(sentiment_score, 1.0)
            
            summary = f"Social Sentiment for {', '.join(keywords[:3])}: {sentiment_score:.2f} (based on {hits} news hits)"
            
            return {
                "source": "SentimentAI",
                "type": "sentiment",
                "summary": summary,
                "confidence": 0.75,
                "relevant_markets": keywords,
                "raw": {"sentiment_score": sentiment_score, "hits": hits}
            }
        except Exception as e:
            logger.error(f"Error fetching social sentiment: {e}")
            return {"source": "SentimentAI", "type": "sentiment", "summary": f"Error: {e}", "confidence": 0.0, "relevant_markets": [], "raw": {}}

    async def fetch_market_volatility(self, market_id: str) -> Dict[str, Any]:
        """
        Layer 6: Calendar + Volatility. Tracks volatility spikes near event starts.
        """
        try:
            # This would fetch historical price data from Polymarket to calculate Z-scores
            # For now, we use a placeholder that simulates volatility analysis
            spike_ratio = await polymarket.detect_volume_spike(market_id)
            
            volatility_z_score = spike_ratio * 1.5 # Simulated Z-score calculation
            
            summary = f"Volatility analysis for {market_id[:10]}: Z-score {volatility_z_score:.2f}"
            if volatility_z_score > 2.0:
                summary += " - HIGH VOLATILITY DETECTED (Potential entry/exit window)"
            
            return {
                "source": "VolatilityMonitor",
                "type": "volatility",
                "summary": summary,
                "confidence": 0.8,
                "relevant_markets": [market_id],
                "raw": {"z_score": volatility_z_score, "spike_ratio": spike_ratio}
            }
        except Exception as e:
            logger.error(f"Error fetching market volatility: {e}")
            return {"source": "VolatilityMonitor", "type": "volatility", "summary": f"Error: {e}", "confidence": 0.0, "relevant_markets": [], "raw": {}}

    async def close(self):
        await self.client.aclose()

signal_fetcher = SignalFetcher()
