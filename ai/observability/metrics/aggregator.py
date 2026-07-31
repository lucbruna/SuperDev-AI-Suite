"""Metrics aggregator."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class MetricsAggregator:
    def __init__(self) -> None:
        self._series: Dict[str, List[float]] = {}
        self._windows: Dict[str, List[Dict[str, Any]]] = {}
    def add(self, name: str, value: float) -> None:
        self._series.setdefault(name, []).append(value)
        if len(self._series[name]) > 1000:
            self._series[name] = self._series[name][-1000:]
    def aggregate(self, name: str, window: int = 60) -> Dict[str, float]:
        values = self._series.get(name, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "sum": 0, "count": 0}
        recent = values[-window:]
        return {"min": min(recent), "max": max(recent), "avg": sum(recent)/len(recent), "sum": sum(recent), "count": len(recent)}
    def percentile(self, name: str, p: float = 95.0) -> float:
        values = sorted(self._series.get(name, []))
        if not values:
            return 0.0
        idx = int(len(values) * p / 100)
        return values[min(idx, len(values)-1)]
    def get_series(self, name: str) -> List[float]:
        return list(self._series.get(name, []))
    def list_names(self) -> List[str]:
        return list(self._series.keys())
    def clear(self, name: str = "") -> int:
        if name:
            n = len(self._series.get(name, []))
            self._series.pop(name, None)
            return n
        n = sum(len(v) for v in self._series.values())
        self._series.clear()
        return n
