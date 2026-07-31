"""Metrics collector for the Data Intelligence Engine."""

from __future__ import annotations

import threading
import time
from typing import Any


class DataIntelligenceMetrics:
    """In-process counters and timings."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, int] = {}
        self._timings: dict[str, list[float]] = {}
        self._gauges: dict[str, float] = {}

    def increment(self, name: str, amount: int = 1) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + amount

    def gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value

    def timing(self, name: str, seconds: float) -> None:
        with self._lock:
            self._timings.setdefault(name, []).append(seconds)

    def timed(self, name: str) -> "_Timer":
        return _Timer(self, name)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            timings = {k: (sum(v) / len(v) if v else 0.0, len(v))
                       for k, v in self._timings.items()}
            return {"counters": dict(self._counters),
                    "timings": timings, "gauges": dict(self._gauges)}


class _Timer:
    def __init__(self, metrics: DataIntelligenceMetrics, name: str) -> None:
        self.metrics = metrics
        self.name = name
        self.started = 0.0

    def __enter__(self) -> "_Timer":
        self.started = time.monotonic()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.metrics.timing(self.name, time.monotonic() - self.started)
