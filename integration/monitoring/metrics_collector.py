"""Metrics collection for integration subsystems."""

from __future__ import annotations

import time
from typing import Any, Callable


class MetricsCollector:
    """Collects counters, gauges, and timings across subsystems."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._timings: dict[str, list[float]] = {}
        self._started: dict[str, float] = {}

    def increment(self, name: str, by: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + by

    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def start_timer(self, name: str) -> None:
        self._started[name] = time.time()

    def stop_timer(self, name: str) -> float:
        elapsed = time.time() - self._started.pop(name, time.time())
        self._timings.setdefault(name, []).append(elapsed)
        return elapsed

    def timed(self, name: str) -> Callable[[], float]:
        self.start_timer(name)
        return lambda: self.stop_timer(name)

    def counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    def gauge(self, name: str) -> float:
        return self._gauges.get(name, 0.0)

    def average_timing(self, name: str) -> float:
        timings = self._timings.get(name, [])
        if not timings:
            return 0.0
        return sum(timings) / len(timings)

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "avg_timings": {k: round(sum(v) / len(v), 4)
                            for k, v in self._timings.items() if v},
        }
