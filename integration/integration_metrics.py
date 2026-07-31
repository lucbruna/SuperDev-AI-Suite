from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Any


class IntegrationMetrics:
    """Accumulates counters, gauges, and timing metrics for the integration engine."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.metrics")
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = defaultdict(float)
        self._timings: dict[str, list[float]] = defaultdict(list)
        self._started = time.monotonic()

    def increment(self, name: str, amount: int = 1) -> None:
        self._counters[name] += amount

    def record(self, name: str, value: float) -> None:
        self._counters[name] += int(value) if isinstance(value, int) else 0

    def set_gauge(self, name: str, value: float) -> None:
        self._gauges[name] = value

    def time(self, name: str) -> "_Timer":
        return _Timer(self, name)

    def add_timing(self, name: str, seconds: float) -> None:
        self._timings[name].append(seconds)

    def get(self, name: str) -> int:
        return self._counters.get(name, 0)

    def gauge(self, name: str) -> float:
        return self._gauges.get(name, 0.0)

    def average_timing(self, name: str) -> float:
        samples = self._timings.get(name, [])
        if not samples:
            return 0.0
        return sum(samples) / len(samples)

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "timings": {k: sum(v) / len(v) if v else 0.0 for k, v in self._timings.items()},
            "uptime_seconds": round(time.monotonic() - self._started, 3),
        }


class _Timer:
    def __init__(self, metrics: IntegrationMetrics, name: str) -> None:
        self._metrics = metrics
        self._name = name
        self._start = time.monotonic()

    def __enter__(self) -> "_Timer":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self._metrics.add_timing(self._name, time.monotonic() - self._start)
