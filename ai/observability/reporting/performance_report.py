"""Performance report."""
from __future__ import annotations

import time
from typing import Any


class PerformanceReport:
    def __init__(self) -> None:
        self._metrics: dict[str, list[float]] = {}
    def record(self, metric_name: str, value: float) -> None:
        self._metrics.setdefault(metric_name, []).append(value)
    def get_summary(self, metric_name: str) -> dict[str, float]:
        values = self._metrics.get(metric_name, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "count": 0}
        return {"min": min(values), "max": max(values), "avg": sum(values)/len(values), "count": len(values)}
    def generate_report(self) -> dict[str, Any]:
        summaries = {name: self.get_summary(name) for name in self._metrics}
        return {"metrics": summaries, "total_metrics": len(self._metrics), "timestamp": time.time()}
    def list_metrics(self) -> list[str]:
        return list(self._metrics.keys())
    def clear(self, metric_name: str = "") -> int:
        if metric_name:
            n = len(self._metrics.get(metric_name, []))
            self._metrics.pop(metric_name, None)
            return n
        n = sum(len(v) for v in self._metrics.values())
        self._metrics.clear()
        return n
