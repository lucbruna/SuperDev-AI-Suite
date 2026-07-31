"""Analytics comparison."""
from __future__ import annotations
from typing import Any, Dict, List

class AnalyticsComparison:
    def __init__(self) -> None:
        self._comparisons: List[Dict[str, Any]] = []
    def compare(self, datasets: Dict[str, Dict[str, float]], metric: str = "value") -> Dict[str, Any]:
        ranked = sorted(datasets.items(), key=lambda x: x[1].get(metric, 0), reverse=True)
        comparison = {"metric": metric, "ranking": [{"dataset": name, "value": data.get(metric, 0)} for name, data in ranked], "best": ranked[0][0] if ranked else ""}
        self._comparisons.append(comparison)
        return comparison
    def diff(self, dataset_a: Dict[str, float], dataset_b: Dict[str, float]) -> Dict[str, Any]:
        diffs = {}
        all_keys = set(list(dataset_a.keys()) + list(dataset_b.keys()))
        for k in all_keys:
            va = dataset_a.get(k, 0)
            vb = dataset_b.get(k, 0)
            diffs[k] = {"a": va, "b": vb, "diff": vb - va}
        return {"diffs": diffs, "total": len(diffs)}
    def get_comparisons(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._comparisons[-limit:]
    def count(self) -> int:
        return len(self._comparisons)
