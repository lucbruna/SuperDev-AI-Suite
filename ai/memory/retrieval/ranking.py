from __future__ import annotations

from collections.abc import Callable
from typing import Any


class Ranking:
    """Ranks retrieval results by score."""

    def __init__(self):
        self._ranking_count: int = 0

    @property
    def ranking_count(self) -> int:
        return self._ranking_count

    def rank(self, items: list[dict[str, Any]], score_key: str = "score") -> list[dict[str, Any]]:
        result = sorted(items, key=lambda x: x.get(score_key, 0), reverse=True)
        for rank, item in enumerate(result, 1):
            item["rank"] = rank
        self._ranking_count += 1
        return result

    def rank_by_field(self, items: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
        result = sorted(items, key=lambda x: x.get(field, ""), reverse=True)
        self._ranking_count += 1
        return result

    def rank_custom(self, items: list[dict[str, Any]], key_fn: Callable) -> list[dict[str, Any]]:
        result = sorted(items, key=key_fn, reverse=True)
        self._ranking_count += 1
        return result

    def top_k(self, items: list[dict[str, Any]], k: int) -> list[dict[str, Any]]:
        return items[:k]

    def reset(self) -> None:
        self._ranking_count = 0
