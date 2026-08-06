"""Embedding configuration — vector dimensions, providers and batching.

Environment prefix: ``SUPERDEV_KG_EMBED_*``.
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
class EmbeddingConfig:
    """Configuration for vector embeddings."""

    enabled: bool = True
    provider: str = "local"  # local | ollama | openai | gemini | claude
    model: str = "default"
    dimension: int = 384
    batch_size: int = 32
    max_tokens_per_chunk: int = 512
    chunk_overlap: int = 32
    normalize: bool = True
    cache_embeddings: bool = True

    # Provider endpoints/keys (empty == not configured).
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "nomic-embed-text"
    openai_api_key: str = ""
    openai_model: str = "text-embedding-3-small"
    gemini_api_key: str = ""
    gemini_model: str = "text-embedding-004"

    @classmethod
    def from_env(cls) -> "EmbeddingConfig":
        cfg = cls()
        cfg.enabled = _env_bool("SUPERDEV_KG_EMBED_ENABLED", cfg.enabled)
        cfg.provider = os.getenv("SUPERDEV_KG_EMBED_PROVIDER", cfg.provider)
        cfg.model = os.getenv("SUPERDEV_KG_EMBED_MODEL", cfg.model)
        cfg.dimension = int(os.getenv("SUPERDEV_KG_EMBED_DIMENSION", str(cfg.dimension)))
        cfg.batch_size = int(os.getenv("SUPERDEV_KG_EMBED_BATCH", str(cfg.batch_size)))
        cfg.ollama_url = os.getenv("SUPERDEV_KG_EMBED_OLLAMA_URL", cfg.ollama_url)
        cfg.openai_api_key = os.getenv("SUPERDEV_KG_EMBED_OPENAI_KEY", cfg.openai_api_key)
        return cfg
