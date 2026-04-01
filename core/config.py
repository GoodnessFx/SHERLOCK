import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Anthropic
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # Polymarket
    POLYMARKET_API_KEY: str = os.getenv("POLYMARKET_API_KEY", "")

    # Signals
    OPENWEATHER_API_KEY: str = os.getenv("OPENWEATHER_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")

    # Monetization
    SOLANA_WALLET_ADDRESS: str = os.getenv("SOLANA_WALLET_ADDRESS", "YourSolanaAddressHere")

    # Server
    API_PORT: int = int(os.getenv("API_PORT", 8000))
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Agent Behavior
    DAEMON_INTERVAL_MINUTES: int = int(os.getenv("DAEMON_INTERVAL_MINUTES", 15))
    MIN_EDGE_THRESHOLD: float = float(os.getenv("MIN_EDGE_THRESHOLD", 0.05))
    MIN_CONFIDENCE_THRESHOLD: float = float(os.getenv("MIN_CONFIDENCE_THRESHOLD", 0.50))
    MAX_MARKETS_PER_RUN: int = int(os.getenv("MAX_MARKETS_PER_RUN", 20))
    MEMORY_RECALL_COUNT: int = int(os.getenv("MEMORY_RECALL_COUNT", 5))

    # Database
    SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", "data/oracle.db")
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "data/chroma")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

settings = Settings()

def validate_config():
    missing = []
    if not settings.ANTHROPIC_API_KEY:
        missing.append("ANTHROPIC_API_KEY")
    if not settings.OPENWEATHER_API_KEY:
        missing.append("OPENWEATHER_API_KEY")
    if not settings.NEWS_API_KEY:
        missing.append("NEWS_API_KEY")
    
    if missing:
        print(f"WARNING: Missing required environment variables: {', '.join(missing)}")
        return False
    return True
