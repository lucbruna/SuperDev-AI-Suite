"""Usage analysis."""

from __future__ import annotations

from typing import Any


class UsageAnalysis:
    def __init__(self) -> None:
        self._usage: dict[str, dict[str, float]] = {}

    def record(self, org_id: str, metric: str, value: float) -> None:
        self._usage.setdefault(org_id, {})
        self._usage[org_id][metric] = self._usage[org_id].get(metric, 0) + value

    def get_usage(self, org_id: str) -> dict[str, float]:
        return dict(self._usage.get(org_id, {}))

    def total_by_metric(self, metric: str) -> float:
        return sum(data.get(metric, 0) for data in self._usage.values())

    def top_by_metric(self, metric: str, limit: int = 10) -> list[dict[str, Any]]:
        usage = [(org, data.get(metric, 0)) for org, data in self._usage.items()]
        sorted_usage = sorted(usage, key=lambda x: x[1], reverse=True)[:limit]
        return [{"org_id": org, "value": val} for org, val in sorted_usage]

    def avg_by_metric(self, metric: str) -> float:
        values = [data.get(metric, 0) for data in self._usage.values() if metric in data]
        return sum(values) / len(values) if values else 0.0

    def list_metrics(self, org_id: str) -> list[str]:
        return list(self._usage.get(org_id, {}).keys())

    def list_orgs(self) -> list[str]:
        return list(self._usage.keys())

    def clear(self, org_id: str = "") -> int:
        if org_id:
            n = len(self._usage.get(org_id, {}))
            self._usage.pop(org_id, None)
            return n
        n = sum(len(v) for v in self._usage.values())
        self._usage.clear()
        return n
