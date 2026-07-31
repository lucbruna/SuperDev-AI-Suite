"""Scenario comparison."""
from __future__ import annotations

from typing import Any


class ScenarioComparison:
    def __init__(self) -> None:
        self._comparisons: list[dict[str, Any]] = []
    def compare(self, scenarios: dict[str, dict[str, Any]], metric: str = "score") -> dict[str, Any]:
        ranked = sorted(scenarios.items(), key=lambda x: x[1].get(metric, 0), reverse=True)
        comparison = {"metric": metric, "ranking": [{"scenario_id": sid, "value": data.get(metric, 0)} for sid, data in ranked], "winner": ranked[0][0] if ranked else ""}
        self._comparisons.append(comparison)
        return comparison
    def diff(self, scenario_a: dict[str, Any], scenario_b: dict[str, Any]) -> dict[str, Any]:
        keys = set(list(scenario_a.keys()) + list(scenario_b.keys()))
        diffs = {}
        for k in keys:
            va = scenario_a.get(k)
            vb = scenario_b.get(k)
            if va != vb:
                diffs[k] = {"a": va, "b": vb}
        return {"diffs": diffs, "total_diffs": len(diffs)}
    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._comparisons[-limit:]
    def best_scenario(self, metric: str = "score") -> str:
        if not self._comparisons:
            return ""
        return self._comparisons[-1].get("winner", "")
    def count(self) -> int:
        return len(self._comparisons)
    def clear(self) -> int:
        n = len(self._comparisons)
        self._comparisons.clear()
        return n
