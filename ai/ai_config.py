from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class AIConfig(BaseSettings):
    model_config = {"env_prefix": "AI_", "case_sensitive": False}

    default_provider: str = "openai"
    max_retries: int = 3
    timeout: int = 60
    streaming_default: bool = True
    model_defaults: dict[str, str] = Field(
        default_factory=lambda: {
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "gemini": "gemini-1.5-pro",
            "ollama": "llama3",
        }
    )
    redis_url: str | None = None
    log_level: str = "INFO"
    embedding_model: str = "text-embedding-3-small"
    max_concurrent_agents: int = 10


@lru_cache
def get_ai_config() -> AIConfig:
    """Get cached AI configuration singleton."""
    return AIConfig()
