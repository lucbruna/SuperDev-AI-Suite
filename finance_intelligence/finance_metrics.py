"""Metrics for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

import threading
import time
from typing import Any


class FinanceMetrics:
    """Thread-safe counters and timings."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, int] = {}
        self._timings: dict[str, list[float]] = {}

    def increment(self, name: str, amount: int = 1) -> None:
        with self._lock:
            self._counters[name] = self._counters.get(name, 0) + amount

    def timing(self, name: str, seconds: float) -> None:
        with self._lock:
            self._timings.setdefault(name, []).append(float(seconds))

    def avg(self, name: str) -> float:
        with self._lock:
            values = self._timings.get(name, [])
        return sum(values) / len(values) if values else 0.0

    def count(self, name: str) -> int:
        with self._lock:
            return self._counters.get(name, 0)

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "counters": dict(self._counters),
                "timings": {name: (sum(values) / len(values) if values
                                   else 0.0)
                            for name, values in self._timings.items()},
            }


class _Timer:
    def __init__(self, metrics: FinanceMetrics, name: str) -> None:
        self.metrics = metrics
        self.name = name
        self.started = time.monotonic()

    def __enter__(self) -> "_Timer":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.metrics.timing(self.name, time.monotonic() - self.started)
