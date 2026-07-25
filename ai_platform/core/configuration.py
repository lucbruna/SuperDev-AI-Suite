from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field
from functools import lru_cache


class AIPlatformConfig(BaseSettings):
    model_config = {"env_prefix": "AI_PLATFORM_", "case_sensitive": False}

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
    redis_url: Optional[str] = None
    log_level: str = "INFO"
    embedding_model: str = "text-embedding-3-small"


@lru_cache
def get_platform_config() -> AIPlatformConfig:
    return AIPlatformConfig()
