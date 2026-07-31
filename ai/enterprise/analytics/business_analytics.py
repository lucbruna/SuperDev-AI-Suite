"""Business analytics."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class BusinessAnalytics:
    def __init__(self) -> None:
        self._metrics: Dict[str, List[Dict[str, Any]]] = {}
    def record(self, metric_name: str, value: float, labels: Dict[str, str] = None) -> None:
        entry = {"value": value, "labels": labels or {}, "timestamp": time.time()}
        self._metrics.setdefault(metric_name, []).append(entry)
        if len(self._metrics[metric_name]) > 10000:
            self._metrics[metric_name] = self._metrics[metric_name][-10000:]
    def get_metric(self, metric_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self._metrics.get(metric_name, [])[-limit:]
    def sum_metric(self, metric_name: str) -> float:
        return sum(e["value"] for e in self._metrics.get(metric_name, []))
    def avg_metric(self, metric_name: str) -> float:
        values = [e["value"] for e in self._metrics.get(metric_name, [])]
        return sum(values) / len(values) if values else 0.0
    def count_metric(self, metric_name: str) -> int:
        return len(self._metrics.get(metric_name, []))
    def list_metrics(self) -> List[str]:
        return list(self._metrics.keys())
    def clear(self, metric_name: str = "") -> int:
        if metric_name:
            n = len(self._metrics.get(metric_name, []))
            self._metrics.pop(metric_name, None)
            return n
        n = sum(len(v) for v in self._metrics.values())
        self._metrics.clear()
        return n
