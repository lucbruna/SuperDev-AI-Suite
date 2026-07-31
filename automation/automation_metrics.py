"""Metrics collection for the automation engine."""

from __future__ import annotations

import time
from typing import Any


class AutomationMetrics:
    """Counters and timings for automation executions."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._timings: dict[str, list[float]] = {}

    def increment(self, name: str, by: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + by

    def record_timing(self, name: str, seconds: float) -> None:
        self._timings.setdefault(name, []).append(seconds)

    def time_block(self, name: str) -> "_Timing":
        return _Timing(self, name)

    def counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    def average(self, name: str) -> float:
        timings = self._timings.get(name, [])
        if not timings:
            return 0.0
        return sum(timings) / len(timings)

    def count_timings(self, name: str) -> int:
        return len(self._timings.get(name, []))

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "averages": {k: round(sum(v) / len(v), 4)
                         for k, v in self._timings.items() if v},
        }


class _Timing:
    def __init__(self, metrics: AutomationMetrics, name: str) -> None:
        self._metrics = metrics
        self._name = name
        self._start = time.monotonic()

    def __enter__(self) -> "_Timing":
        return self

    def __exit__(self, *_: Any) -> None:
        self._metrics.record_timing(self._name, time.monotonic() - self._start)
