from __future__ import annotations

import logging
from typing import Any

from ..knowledge_models import SearchResult
from .search_engine import SearchEngine


class SearchManager:
    """High-level facade for the knowledge search subsystem."""

    def __init__(self, engine: SearchEngine | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.search.manager")
        self.engine = engine or SearchEngine()

    def search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        return self.engine.search(query, top_k=top_k)

    def keyword_only(self, query: str, top_k: int = 5) -> list[SearchResult]:
        return self.engine.keyword.search(query, top_k=top_k)

    def semantic_only(self, query: str, top_k: int = 5) -> list[SearchResult]:
        return self.engine.semantic.search(query, top_k=top_k)

    def stats(self) -> dict[str, Any]:
        return {
            "index_terms": self.engine.index_manager.keyword.count(),
            "vectors": self.engine.vector_store.count(),
        }
