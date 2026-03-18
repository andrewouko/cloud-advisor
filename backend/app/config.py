"""Application configuration via pydantic-settings.

All settings are loaded from environment variables (or a .env file).
Use `get_settings()` everywhere — it is cached via lru_cache so the
.env file is only parsed once per process.
"""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Claude / Anthropic
    anthropic_api_key: str

    # Model configuration
    model_name: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 1024
    temperature: float = 0.7

    # CORS — comma-separated list of allowed origins
    allowed_origins: str = "http://localhost:3000"

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cloudadvisor"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # App metadata
    app_name: str = "CloudAdvisor API"
    app_version: str = "1.0.0"
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @model_validator(mode="after")
    def normalize_database_url(self) -> "Settings":
        """Rewrite provider-supplied DATABASE_URL to use the asyncpg driver."""
        url = self.database_url
        if url.startswith("postgresql://"):
            self.database_url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            self.database_url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
