"""Storage abstraction for the Architecture Graph.

The default backend is SQLite (stdlib). PostgreSQL and Neo4j backends are
provided as adapters that activate when the corresponding drivers are
installed and configured; all backends implement :class:`GraphStorage`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


class GraphStorage(ABC):
    """Interface implemented by every persistence backend."""

    backend_name = "base"

    @abstractmethod
    def save(self, graph: ArchitectureGraph) -> None:
        """Persist the graph (replacing the previous snapshot)."""

    @abstractmethod
    def load(self) -> ArchitectureGraph | None:
        """Return the persisted graph or None when empty."""

    @abstractmethod
    def exists(self) -> bool:
        """Return True when a graph snapshot is present."""

    @abstractmethod
    def clear(self) -> None:
        """Remove the persisted snapshot."""


def get_storage(backend: str = "") -> GraphStorage:
    """Factory selecting a storage backend by name (default: sqlite)."""
    from modules.architecture_graph.config.graph_settings import get_settings

    cfg = get_settings().config
    backend = backend or cfg.storage_backend

    if backend == "sqlite":
        from modules.architecture_graph.storage.sqlite_storage import SQLiteGraphStorage

        return SQLiteGraphStorage(cfg.db_path)
    if backend == "postgres":
        from modules.architecture_graph.storage.postgres_storage import PostgresGraphStorage

        return PostgresGraphStorage(
            url=cfg.postgres_url if hasattr(cfg, "postgres_url") else ""
        )
    if backend == "neo4j":
        from modules.architecture_graph.storage.neo4j_storage import Neo4jGraphStorage

        return Neo4jGraphStorage(
            uri=cfg.neo4j_uri if hasattr(cfg, "neo4j_uri") else "",
            user=cfg.neo4j_user if hasattr(cfg, "neo4j_user") else "",
            password=cfg.neo4j_password if hasattr(cfg, "neo4j_password") else "",
        )

    # Default / unknown backend: memory (no persistence).
    from modules.architecture_graph.storage.sqlite_storage import MemoryGraphStorage

    return MemoryGraphStorage()
