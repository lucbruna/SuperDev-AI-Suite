"""Analytics comparison."""
from __future__ import annotations

from typing import Any


class AnalyticsComparison:
    def __init__(self) -> None:
        self._comparisons: list[dict[str, Any]] = []
    def compare(self, datasets: dict[str, dict[str, float]], metric: str = "value") -> dict[str, Any]:
        ranked = sorted(datasets.items(), key=lambda x: x[1].get(metric, 0), reverse=True)
        comparison = {"metric": metric, "ranking": [{"dataset": name, "value": data.get(metric, 0)} for name, data in ranked], "best": ranked[0][0] if ranked else ""}
        self._comparisons.append(comparison)
        return comparison
    def diff(self, dataset_a: dict[str, float], dataset_b: dict[str, float]) -> dict[str, Any]:
        diffs = {}
        all_keys = set(list(dataset_a.keys()) + list(dataset_b.keys()))
        for k in all_keys:
            va = dataset_a.get(k, 0)
            vb = dataset_b.get(k, 0)
            diffs[k] = {"a": va, "b": vb, "diff": vb - va}
        return {"diffs": diffs, "total": len(diffs)}
    def get_comparisons(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._comparisons[-limit:]
    def count(self) -> int:
        return len(self._comparisons)
