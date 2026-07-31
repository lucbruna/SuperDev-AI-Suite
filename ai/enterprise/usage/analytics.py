"""Usage analytics."""
from __future__ import annotations

import statistics


class UsageAnalytics:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, list[float]]] = {}
    def record(self, org_id: str, metric: str, value: float) -> None:
        self._data.setdefault(org_id, {}).setdefault(metric, []).append(value)
        if len(self._data[org_id][metric]) > 1000:
            self._data[org_id][metric] = self._data[org_id][metric][-1000:]
    def analyze(self, org_id: str, metric: str) -> dict[str, float]:
        values = self._data.get(org_id, {}).get(metric, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "total": 0, "count": 0}
        return {"min": min(values), "max": max(values), "avg": statistics.mean(values), "total": sum(values), "count": len(values)}
    def trend(self, org_id: str, metric: str) -> str:
        values = self._data.get(org_id, {}).get(metric, [])
        if len(values) < 3:
            return "insufficient_data"
        recent = values[-5:]
        if all(recent[i] <= recent[i+1] for i in range(len(recent)-1)):
            return "increasing"
        if all(recent[i] >= recent[i+1] for i in range(len(recent)-1)):
            return "decreasing"
        return "stable"
    def list_metrics(self, org_id: str) -> list[str]:
        return list(self._data.get(org_id, {}).keys())
    def get_values(self, org_id: str, metric: str) -> list[float]:
        return list(self._data.get(org_id, {}).get(metric, []))
    def compare_orgs(self, metric: str) -> dict[str, float]:
        return {org: sum(data.get(metric, [0])) for org, data in self._data.items()}
