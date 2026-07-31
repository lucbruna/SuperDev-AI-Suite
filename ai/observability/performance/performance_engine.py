"""Performance engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class PerformanceEngine:
    def __init__(self) -> None:
        self._benchmarks: Dict[str, List[float]] = {}
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def record_benchmark(self, name: str, duration_ms: float) -> None:
        self._benchmarks.setdefault(name, []).append(duration_ms)
        if len(self._benchmarks[name]) > 1000:
            self._benchmarks[name] = self._benchmarks[name][-1000:]
    def get_benchmark_stats(self, name: str) -> Dict[str, float]:
        values = self._benchmarks.get(name, [])
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "count": 0}
        return {"min": min(values), "max": max(values), "avg": sum(values)/len(values), "count": len(values)}
    def get_status(self) -> Dict[str, Any]:
        return {"running": self._started, "benchmarks": len(self._benchmarks)}
