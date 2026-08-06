"""Index manager — register and query named knowledge indexes.

Light wrapper around indexer instances so callers can build multiple named
indexes and route queries through one entry point.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.indexing.indexer import KnowledgeIndexer


class IndexManager:
    """Manages a set of named knowledge indexers."""

    def __init__(self) -> None:
        self._indexers: dict[str, KnowledgeIndexer] = {}

    def register(self, name: str, indexer: KnowledgeIndexer) -> "IndexManager":
        """Register an indexer under ``name`` (returns self for chaining)."""
        self._indexers[name] = indexer
        return self

    @classmethod
    def default(cls) -> "IndexManager":
        """An index manager pre-loaded with the composite indexer."""
        return cls().register("composite", KnowledgeIndexer())

    @property
    def names(self) -> list[str]:
        return sorted(self._indexers)

    def build_all(self, ctx) -> dict[str, Any]:
        """Run every registered indexer against the context."""
        return {name: indexer.index(ctx) for name, indexer in self._indexers.items()}

    def query(self, name: str, text: str, ctx) -> dict[str, Any]:
        """Route a query to the named indexer."""
        indexer = self._indexers.get(name)
        if indexer is None:
            raise KeyError(f"no indexer named {name!r}")
        return indexer.query(text, ctx)

    def stats(self, ctx) -> dict[str, Any]:
        """Stats of the current composite search index, if built."""
        index = ctx.memory.get("search_index")
        return index.get("stats", {}) if index else {}
