"""Cache configuration — cache backends and TTLs.

Environment prefix: ``SUPERDEV_KG_CACHE_*``.
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
class CacheConfig:
    """Configuration for graph/embedding/semantic/query caches."""

    enabled: bool = True
    backend: str = "memory"  # memory | redis
    redis_url: str = ""
    redis_prefix: str = "superdev:kg:"
    default_ttl_seconds: int = 300
    graph_ttl_seconds: int = 900
    embedding_ttl_seconds: int = 3600
    semantic_ttl_seconds: int = 1800
    query_ttl_seconds: int = 60
    max_memory_entries: int = 100_000
    eviction_policy: str = "lru"  # lru | fifo | none

    @classmethod
    def from_env(cls) -> "CacheConfig":
        cfg = cls()
        cfg.enabled = _env_bool("SUPERDEV_KG_CACHE_ENABLED", cfg.enabled)
        cfg.backend = os.getenv("SUPERDEV_KG_CACHE_BACKEND", cfg.backend)
        cfg.redis_url = os.getenv("SUPERDEV_KG_CACHE_REDIS_URL", cfg.redis_url)
        cfg.default_ttl_seconds = int(
            os.getenv("SUPERDEV_KG_CACHE_TTL", str(cfg.default_ttl_seconds))
        )
        return cfg
