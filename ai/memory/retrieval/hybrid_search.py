from __future__ import annotations

from typing import Any, Dict, List

from .keyword_search import KeywordSearch
from .semantic_search import SemanticSearch


class HybridSearch:
    """Hybrid search combining keyword and semantic approaches."""

    def __init__(self, keyword_weight: float = 0.5, semantic_weight: float = 0.5):
        self._keyword = KeywordSearch()
        self._semantic = SemanticSearch()
        self._keyword_weight = keyword_weight
        self._semantic_weight = semantic_weight
        self._search_count: int = 0

    @property
    def search_count(self) -> int:
        return self._search_count

    def search(self, query: str, entries: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        kw_results = self._keyword.search(query, entries)
        sem_results = self._semantic.search(query, entries, top_k * 2)
        combined: dict = {}
        for rank, entry in enumerate(kw_results):
            eid = id(entry)
            combined[eid] = (combined.get(eid, (0, 0))[0] + self._keyword_weight * (1.0 / (rank + 1)), entry)
        for rank, entry in enumerate(sem_results):
            eid = id(entry)
            combined[eid] = (combined.get(eid, (0, 0))[0] + self._semantic_weight * (1.0 / (rank + 1)), entry)
        ranked = sorted(combined.values(), key=lambda x: x[0], reverse=True)
        self._search_count += 1
        return [entry for score, entry in ranked[:top_k]]

    def reset(self) -> None:
        self._keyword.reset()
        self._semantic.reset()
        self._search_count = 0
