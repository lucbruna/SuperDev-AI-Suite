"""Metrics storage."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class MetricsStorage:
    def __init__(self, max_series: int = 10000, max_points: int = 1000) -> None:
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self._max_series = max_series
        self._max_points = max_points
    def store(self, name: str, value: float, labels: Optional[Dict[str, str]] = None, timestamp: float = 0.0) -> bool:
        point = {"value": value, "timestamp": timestamp or time.time(), "labels": labels or {}}
        self._data.setdefault(name, []).append(point)
        if len(self._data[name]) > self._max_points:
            self._data[name] = self._data[name][-self._max_points:]
        return True
    def query(self, name: str, start: float = 0, end: float = 0) -> List[Dict[str, Any]]:
        points = self._data.get(name, [])
        if start:
            points = [p for p in points if p["timestamp"] >= start]
        if end:
            points = [p for p in points if p["timestamp"] <= end]
        return points
    def get_latest(self, name: str) -> Optional[float]:
        points = self._data.get(name, [])
        return points[-1]["value"] if points else None
    def list_names(self) -> List[str]:
        return list(self._data.keys())
    def clear(self, name: str = "") -> int:
        if name:
            n = len(self._data.get(name, []))
            self._data.pop(name, None)
            return n
        n = sum(len(v) for v in self._data.values())
        self._data.clear()
        return n
