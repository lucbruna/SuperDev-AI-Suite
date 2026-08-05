"""Configuration model for the Architecture Graph module.

Uses plain dataclasses + environment overrides so the module has zero hard
dependencies beyond the standard library. Values follow the naming scheme
``SUPERDEV_GRAPH_<KEY>`` (e.g. ``SUPERDEV_GRAPH_SCAN_FRONTEND=1``).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from modules.architecture_graph.config.graph_constants import (
    DEFAULT_DATA_DIR_NAME,
    DEFAULT_DB_FILE,
    DEFAULT_EXPORT_DIR,
    DEFAULT_SNAPSHOT_FILE,
    FRONTEND_DIRS,
    IGNORE_DIRS,
    IGNORE_FILES,
    PROJECT_DIRS,
)


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class GraphConfig:
    """Runtime configuration for graph scanning and analysis."""

    project_root: str = ""
    project_dirs: tuple[str, ...] = PROJECT_DIRS
    frontend_dirs: tuple[str, ...] = FRONTEND_DIRS
    ignore_dirs: frozenset[str] = IGNORE_DIRS
    ignore_files: frozenset[str] = IGNORE_FILES

    # Scan behaviour
    scan_frontend: bool = True
    max_files: int = 20000          # safety cap for huge repositories
    max_file_size: int = 1_500_000  # bytes; skip pathological files
    follow_symlinks: bool = False
    include_hidden: bool = False

    # Storage
    data_dir: str = ""
    db_file: str = DEFAULT_DB_FILE
    snapshot_file: str = DEFAULT_SNAPSHOT_FILE
    export_dir: str = DEFAULT_EXPORT_DIR
    storage_backend: str = "sqlite"  # sqlite | postgres | neo4j | memory

    # Optional external backends (empty == not configured)
    postgres_url: str = ""
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""
    redis_url: str = ""

    # Derived (filled by resolve())
    db_path: str = ""
    snapshot_path: str = ""
    export_path: str = ""

    # Analysis
    impact_max_depth: int = 12
    analyze_duplicates: bool = True
    duplicate_similarity_threshold: float = 0.8

    # Graph model
    name: str = "superdev"
    version: int = 1

    @classmethod
    def from_env(cls) -> "GraphConfig":
        cfg = cls()
        cfg.scan_frontend = _env_bool("SUPERDEV_GRAPH_SCAN_FRONTEND", cfg.scan_frontend)
        cfg.storage_backend = os.getenv("SUPERDEV_GRAPH_STORAGE", cfg.storage_backend)
        cfg.postgres_url = os.getenv("SUPERDEV_GRAPH_POSTGRES_URL", cfg.postgres_url)
        cfg.neo4j_uri = os.getenv("SUPERDEV_GRAPH_NEO4J_URI", cfg.neo4j_uri)
        cfg.neo4j_user = os.getenv("SUPERDEV_GRAPH_NEO4J_USER", cfg.neo4j_user)
        cfg.neo4j_password = os.getenv("SUPERDEV_GRAPH_NEO4J_PASSWORD", cfg.neo4j_password)
        cfg.redis_url = os.getenv("SUPERDEV_GRAPH_REDIS_URL", cfg.redis_url)
        cfg.max_files = int(os.getenv("SUPERDEV_GRAPH_MAX_FILES", str(cfg.max_files)))
        cfg.impact_max_depth = int(
            os.getenv("SUPERDEV_GRAPH_IMPACT_DEPTH", str(cfg.impact_max_depth))
        )
        cfg.analyze_duplicates = _env_bool(
            "SUPERDEV_GRAPH_DUPLICATES", cfg.analyze_duplicates
        )
        return cfg

    def resolve(self, project_root: str | None = None) -> None:
        """Resolve project root and derived paths."""
        if project_root:
            self.project_root = str(Path(project_root).resolve())
        if not self.project_root:
            # Default to the repository root (two levels up from this file).
            self.project_root = str(
                Path(__file__).resolve().parent.parent.parent.parent
            )
        base = Path(self.project_root) / DEFAULT_DATA_DIR_NAME / "architecture_graph"
        if not self.data_dir:
            self.data_dir = str(base)
        self.db_path = str(Path(self.data_dir) / self.db_file)
        self.snapshot_path = str(Path(self.data_dir) / self.snapshot_file)
        self.export_path = str(Path(self.data_dir) / self.export_dir)

    @property
    def scan_dirs(self) -> tuple[str, ...]:
        dirs = list(self.project_dirs)
        if self.scan_frontend:
            dirs.extend(self.frontend_dirs)
        return tuple(dirs)
