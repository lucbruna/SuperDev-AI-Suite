from __future__ import annotations

from typing import Any, Callable, Dict, List


class Reranking:
    """Re-ranks retrieval results with alternative strategies."""

    def __init__(self):
        self._reranking_count: int = 0

    @property
    def reranking_count(self) -> int:
        return self._reranking_count

    def rerank(self, query: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        q_words = set(query.lower().split())
        scored: List[tuple] = []
        for item in items:
            content = str(item.get("content", "")).lower()
            word_overlap = len(q_words & set(content.split()))
            scored.append((word_overlap, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        self._reranking_count += 1
        return [item for _, item in scored]

    def rerank_by_metric(self, items: List[Dict[str, Any]], metric_key: str = "relevance") -> List[Dict[str, Any]]:
        result = sorted(items, key=lambda x: x.get(metric_key, 0), reverse=True)
        self._reranking_count += 1
        return result

    def rerank_custom(self, items: List[Dict[str, Any]], fn: Callable) -> List[Dict[str, Any]]:
        scored = [(fn(item), item) for item in items]
        scored.sort(key=lambda x: x[0], reverse=True)
        self._reranking_count += 1
        return [item for _, item in scored]

    def reset(self) -> None:
        self._reranking_count = 0
