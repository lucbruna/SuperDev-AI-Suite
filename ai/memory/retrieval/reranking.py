from __future__ import annotations

from collections.abc import Callable
from typing import Any


class Reranking:
    """Re-ranks retrieval results with alternative strategies."""

    def __init__(self):
        self._reranking_count: int = 0

    @property
    def reranking_count(self) -> int:
        return self._reranking_count

    def rerank(self, query: str, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        q_words = set(query.lower().split())
        scored: list[tuple] = []
        for item in items:
            content = str(item.get("content", "")).lower()
            word_overlap = len(q_words & set(content.split()))
            scored.append((word_overlap, item))
        scored.sort(key=lambda x: x[0], reverse=True)
        self._reranking_count += 1
        return [item for _, item in scored]

    def rerank_by_metric(self, items: list[dict[str, Any]], metric_key: str = "relevance") -> list[dict[str, Any]]:
        result = sorted(items, key=lambda x: x.get(metric_key, 0), reverse=True)
        self._reranking_count += 1
        return result

    def rerank_custom(self, items: list[dict[str, Any]], fn: Callable) -> list[dict[str, Any]]:
        scored = [(fn(item), item) for item in items]
        scored.sort(key=lambda x: x[0], reverse=True)
        self._reranking_count += 1
        return [item for _, item in scored]

    def reset(self) -> None:
        self._reranking_count = 0
