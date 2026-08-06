"""Database configuration — storage backends for the knowledge graph.

Environment prefix: ``SUPERDEV_KG_DB_*``.
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
class DatabaseConfig:
    """Configuration for graph persistence and auxiliary stores."""

    backend: str = "sqlite"  # sqlite | postgres | neo4j | redis | memory

    sqlite_path: str = ""
    postgres_url: str = ""
    postgres_pool_size: int = 5
    postgres_pool_max_overflow: int = 10
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""
    redis_url: str = ""
    vector_backend: str = "memory"  # memory | redis | postgres
    vector_dimension: int = 384

    pool_timeout_seconds: int = 30
    connection_max_retries: int = 3
    migrations_enabled: bool = True
    backup_on_write: bool = False

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        cfg = cls()
        cfg.backend = os.getenv("SUPERDEV_KG_DB_BACKEND", cfg.backend)
        cfg.sqlite_path = os.getenv("SUPERDEV_KG_DB_SQLITE", cfg.sqlite_path)
        cfg.postgres_url = os.getenv("SUPERDEV_KG_DB_POSTGRES_URL", cfg.postgres_url)
        cfg.neo4j_uri = os.getenv("SUPERDEV_KG_DB_NEO4J_URI", cfg.neo4j_uri)
        cfg.neo4j_user = os.getenv("SUPERDEV_KG_DB_NEO4J_USER", cfg.neo4j_user)
        cfg.neo4j_password = os.getenv("SUPERDEV_KG_DB_NEO4J_PASSWORD", cfg.neo4j_password)
        cfg.redis_url = os.getenv("SUPERDEV_KG_DB_REDIS_URL", cfg.redis_url)
        cfg.vector_backend = os.getenv("SUPERDEV_KG_DB_VECTOR_BACKEND", cfg.vector_backend)
        cfg.migrations_enabled = _env_bool("SUPERDEV_KG_DB_MIGRATIONS", cfg.migrations_enabled)
        return cfg
