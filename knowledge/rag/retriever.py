from __future__ import annotations

import logging
from collections.abc import Callable

from ..knowledge_models import SearchResult


class Retriever:
    """Retrieves top-k search results for a query through a pluggable search function."""

    def __init__(
        self,
        search_fn: Callable[[str, int], list[SearchResult]] | None = None,
        threshold: float = 0.0,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.rag.retriever")
        self._search_fn = search_fn
        self._threshold = threshold

    def retrieve(self, query: str, top_k: int = 5) -> list[SearchResult]:
        if self._search_fn is None:
            return []
        results = self._search_fn(query, top_k)
        filtered = [result for result in results if result.score >= self._threshold]
        filtered.sort(key=lambda result: result.score, reverse=True)
        return filtered[:top_k]
