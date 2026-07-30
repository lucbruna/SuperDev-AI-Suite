from __future__ import annotations

from typing import Any, Callable, Dict, List, Tuple


class Ranking:
    """Ranks retrieval results by score."""

    def __init__(self):
        self._ranking_count: int = 0

    @property
    def ranking_count(self) -> int:
        return self._ranking_count

    def rank(self, items: List[Dict[str, Any]], score_key: str = "score") -> List[Dict[str, Any]]:
        result = sorted(items, key=lambda x: x.get(score_key, 0), reverse=True)
        for rank, item in enumerate(result, 1):
            item["rank"] = rank
        self._ranking_count += 1
        return result

    def rank_by_field(self, items: List[Dict[str, Any]], field: str) -> List[Dict[str, Any]]:
        result = sorted(items, key=lambda x: x.get(field, ""), reverse=True)
        self._ranking_count += 1
        return result

    def rank_custom(self, items: List[Dict[str, Any]], key_fn: Callable) -> List[Dict[str, Any]]:
        result = sorted(items, key=key_fn, reverse=True)
        self._ranking_count += 1
        return result

    def top_k(self, items: List[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
        return items[:k]

    def reset(self) -> None:
        self._ranking_count = 0
