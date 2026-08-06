"""LLM configuration — providers, timeouts and prompt settings.

Environment prefix: ``SUPERDEV_AD_LLM_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _env_float(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw.strip())
    except ValueError:
        return default


@dataclass(slots=True)
class LLMConfig:
    """Configuration for LLM-backed reasoning and generation."""

    enabled: bool = False
    provider: str = "ollama"  # ollama | openai | gemini | claude | local
    model: str = ""

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    claude_api_key: str = ""
    claude_model: str = "claude-3-5-haiku-latest"

    timeout_seconds: int = 60
    max_retries: int = 2
    temperature: float = 0.2
    max_tokens: int = 4096
    max_context_tokens: int = 24_000
    stream: bool = False
    fallback_to_echo: bool = True

    @classmethod
    def from_env(cls) -> LLMConfig:
        cfg = cls()
        cfg.enabled = _env_bool("SUPERDEV_AD_LLM_ENABLED", cfg.enabled)
        cfg.provider = os.getenv("SUPERDEV_AD_LLM_PROVIDER", cfg.provider)
        cfg.model = os.getenv("SUPERDEV_AD_LLM_MODEL", cfg.model)
        cfg.ollama_url = os.getenv("SUPERDEV_AD_LLM_OLLAMA_URL", cfg.ollama_url)
        cfg.openai_api_key = os.getenv("SUPERDEV_AD_LLM_OPENAI_KEY", cfg.openai_api_key)
        cfg.openai_base_url = os.getenv(
            "SUPERDEV_AD_LLM_OPENAI_BASE_URL", cfg.openai_base_url
        )
        cfg.gemini_api_key = os.getenv("SUPERDEV_AD_LLM_GEMINI_KEY", cfg.gemini_api_key)
        cfg.claude_api_key = os.getenv("SUPERDEV_AD_LLM_CLAUDE_KEY", cfg.claude_api_key)
        cfg.timeout_seconds = _env_int("SUPERDEV_AD_LLM_TIMEOUT", cfg.timeout_seconds)
        cfg.temperature = _env_float("SUPERDEV_AD_LLM_TEMPERATURE", cfg.temperature)
        cfg.max_tokens = _env_int("SUPERDEV_AD_LLM_MAX_TOKENS", cfg.max_tokens)
        cfg.stream = _env_bool("SUPERDEV_AD_LLM_STREAM", cfg.stream)
        cfg.fallback_to_echo = _env_bool(
            "SUPERDEV_AD_LLM_FALLBACK_ECHO", cfg.fallback_to_echo
        )
        return cfg
