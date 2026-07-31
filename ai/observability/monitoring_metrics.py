"""Metrics collection and storage."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class MetricsCollector:
    def __init__(self, max_series: int = 10000) -> None:
        self._series: Dict[str, List[Dict[str, Any]]] = {}
        self._max = max_series
    def record(self, name: str, value: float, labels: Optional[Dict[str, str]] = None, metric_type: str = "gauge") -> None:
        point = {"name": name, "value": value, "timestamp": time.time(), "labels": labels or {}, "type": metric_type}
        self._series.setdefault(name, []).append(point)
        if len(self._series[name]) > self._max:
            self._series[name] = self._series[name][-self._max:]
    def increment(self, name: str, amount: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        current = self.get_latest(name)
        self.record(name, (current or 0.0) + amount, labels, "counter")
    def get_latest(self, name: str) -> Optional[float]:
        points = self._series.get(name, [])
        return points[-1]["value"] if points else None
    def get_series(self, name: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self._series.get(name, [])[-limit:]
    def get_all_names(self) -> List[str]:
        return list(self._series.keys())
    def aggregate(self, name: str, window: int = 60) -> Dict[str, float]:
        points = self._series.get(name, [])
        if not points:
            return {"min": 0, "max": 0, "avg": 0, "count": 0}
        cutoff = time.time() - window
        recent = [p["value"] for p in points if p["timestamp"] >= cutoff]
        if not recent:
            return {"min": 0, "max": 0, "avg": 0, "count": 0}
        return {"min": min(recent), "max": max(recent), "avg": sum(recent) / len(recent), "count": len(recent)}
    def clear(self, name: str = "") -> int:
        if name:
            n = len(self._series.get(name, []))
            self._series.pop(name, None)
            return n
        n = sum(len(v) for v in self._series.values())
        self._series.clear()
        return n
