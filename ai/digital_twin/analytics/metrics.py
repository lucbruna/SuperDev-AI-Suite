"""Analytics metrics."""
from __future__ import annotations

from typing import Any


class AnalyticsMetrics:
    def __init__(self) -> None:
        self._metrics: dict[str, list[float]] = {}
    def record(self, name: str, value: float) -> None:
        self._metrics.setdefault(name, []).append(value)
    def get(self, name: str) -> dict[str, Any]:
        values = self._metrics.get(name, [])
        if not values:
            return {"error": "no_data"}
        return {"name": name, "min": min(values), "max": max(values), "avg": sum(values)/len(values), "count": len(values)}
    def summary(self) -> dict[str, Any]:
        return {name: {"avg": sum(v)/len(v), "count": len(v)} for name, v in self._metrics.items()}
    def list_metrics(self) -> list[str]:
        return list(self._metrics.keys())
    def clear(self) -> int:
        n = sum(len(v) for v in self._metrics.values())
        self._metrics.clear()
        return n
    def count(self) -> int:
        return len(self._metrics)
