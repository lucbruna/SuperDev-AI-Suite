"""Knowledge pipeline configuration — scan, build and snapshot behaviour.

Central config used by the knowledge engine. Environment prefix:
``SUPERDEV_KG_*``.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from modules.ai_code_knowledge_graph.config.constants import (
    DATA_DIR_NAME,
    DEFAULT_DB_FILE,
    DEFAULT_EXPORT_DIR,
    DEFAULT_SNAPSHOT_FILE,
    DEFAULT_VECTOR_DIR,
    MODULE_DATA_DIR,
)
from modules.ai_code_knowledge_graph.config.scanner_config import ScannerConfig


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class KnowledgeConfig:
    """Top-level configuration for the knowledge graph pipeline."""

    scanner: ScannerConfig = field(default_factory=ScannerConfig)

    name: str = "superdev"
    version: int = 1

    # Pipeline stages (enable/disable).
    run_parsers: bool = True
    run_semantic: bool = True
    run_embeddings: bool = True
    run_relations: bool = True
    run_indexing: bool = True

    # Storage.
    data_dir: str = ""
    db_file: str = DEFAULT_DB_FILE
    snapshot_file: str = DEFAULT_SNAPSHOT_FILE
    export_dir: str = DEFAULT_EXPORT_DIR
    vector_dir: str = DEFAULT_VECTOR_DIR
    storage_backend: str = "sqlite"  # sqlite | postgres | neo4j | redis | memory

    # Optional external backends (empty == not configured).
    postgres_url: str = ""
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""
    redis_url: str = ""

    # Persistence.
    autosave_snapshot: bool = True
    max_snapshots: int = 20

    @classmethod
    def from_env(cls) -> "KnowledgeConfig":
        cfg = cls()
        cfg.scanner = ScannerConfig.from_env()
        cfg.run_semantic = _env_bool("SUPERDEV_KG_SEMANTIC", cfg.run_semantic)
        cfg.run_embeddings = _env_bool("SUPERDEV_KG_EMBEDDINGS", cfg.run_embeddings)
        cfg.run_relations = _env_bool("SUPERDEV_KG_RELATIONS", cfg.run_relations)
        cfg.run_indexing = _env_bool("SUPERDEV_KG_INDEXING", cfg.run_indexing)
        cfg.storage_backend = os.getenv("SUPERDEV_KG_STORAGE", cfg.storage_backend)
        cfg.postgres_url = os.getenv("SUPERDEV_KG_POSTGRES_URL", cfg.postgres_url)
        cfg.neo4j_uri = os.getenv("SUPERDEV_KG_NEO4J_URI", cfg.neo4j_uri)
        cfg.neo4j_user = os.getenv("SUPERDEV_KG_NEO4J_USER", cfg.neo4j_user)
        cfg.neo4j_password = os.getenv("SUPERDEV_KG_NEO4J_PASSWORD", cfg.neo4j_password)
        cfg.redis_url = os.getenv("SUPERDEV_KG_REDIS_URL", cfg.redis_url)
        return cfg

    def resolve(self, project_root: str | None = None) -> None:
        """Resolve project root, data dir and derived storage paths."""
        self.scanner.resolve(project_root)
        root = self.scanner.project_root
        if not self.data_dir:
            self.data_dir = str(
                __import__("pathlib").Path(root) / DATA_DIR_NAME / MODULE_DATA_DIR
            )
