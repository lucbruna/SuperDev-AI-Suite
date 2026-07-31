"""Model comparison."""

from __future__ import annotations

from typing import Any


class ModelComparison:
    def __init__(self) -> None:
        self._comparisons: list[dict[str, Any]] = []

    def compare(self, model_results: dict[str, dict[str, float]], metric: str = "avg_score") -> dict[str, Any]:
        ranked = sorted(model_results.items(), key=lambda x: x[1].get(metric, 0), reverse=True)
        comparison = {
            "metric": metric,
            "ranking": [{"model_id": mid, "score": scores.get(metric, 0)} for mid, scores in ranked],
            "winner": ranked[0][0] if ranked else "",
        }
        self._comparisons.append(comparison)
        return comparison

    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._comparisons[-limit:]

    def winner_count(self, model_id: str) -> int:
        return sum(1 for c in self._comparisons if c.get("winner") == model_id)

    def list_winners(self) -> list[str]:
        return [c["winner"] for c in self._comparisons if c.get("winner")]

    def count(self) -> int:
        return len(self._comparisons)

    def clear(self) -> int:
        n = len(self._comparisons)
        self._comparisons.clear()
        return n
