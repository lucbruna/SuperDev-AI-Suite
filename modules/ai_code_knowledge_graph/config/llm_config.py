"""LLM configuration — providers, timeouts and prompt settings.

Environment prefix: ``SUPERDEV_KG_LLM_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class LLMConfig:
    """Configuration for LLM-backed reasoning and RAG."""

    enabled: bool = False
    provider: str = "ollama"  # ollama | openai | gemini | claude | local
    model: str = ""

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    claude_api_key: str = ""
    claude_model: str = "claude-3-5-haiku-latest"

    timeout_seconds: int = 60
    max_retries: int = 2
    temperature: float = 0.2
    max_tokens: int = 2048

    max_context_tokens: int = 12_000
    prompt_cache_enabled: bool = True
    stream: bool = False

    @classmethod
    def from_env(cls) -> "LLMConfig":
        cfg = cls()
        cfg.enabled = _env_bool("SUPERDEV_KG_LLM_ENABLED", cfg.enabled)
        cfg.provider = os.getenv("SUPERDEV_KG_LLM_PROVIDER", cfg.provider)
        cfg.model = os.getenv("SUPERDEV_KG_LLM_MODEL", cfg.model)
        cfg.ollama_url = os.getenv("SUPERDEV_KG_LLM_OLLAMA_URL", cfg.ollama_url)
        cfg.openai_api_key = os.getenv("SUPERDEV_KG_LLM_OPENAI_KEY", cfg.openai_api_key)
        cfg.gemini_api_key = os.getenv("SUPERDEV_KG_LLM_GEMINI_KEY", cfg.gemini_api_key)
        cfg.claude_api_key = os.getenv("SUPERDEV_KG_LLM_CLAUDE_KEY", cfg.claude_api_key)
        cfg.timeout_seconds = int(os.getenv("SUPERDEV_KG_LLM_TIMEOUT", str(cfg.timeout_seconds)))
        return cfg
