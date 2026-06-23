"""Application configuration loaded from environment / .env."""
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "FundArb API"
    env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    cors_origins: List[str] = ["http://localhost:3000"]

    # Server-side encryption key for API key vault (Fernet).
    vault_key: Optional[str] = None

    # Funding feed
    mock_feed: bool = True
    feed_interval_sec: float = 1.5


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
