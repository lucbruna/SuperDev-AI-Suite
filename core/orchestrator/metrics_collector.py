"""Metrics Collector — system-wide metrics aggregation for the orchestrator."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any


class MetricsCollector:
    """Collects and aggregates system-wide metrics.

    Provides counter increments, gauge tracking, histogram recording,
    and periodic snapshots for observability.
    """

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._max_histogram_size = 1000

    async def increment(self, name: str, value: int = 1) -> int:
        """Increment a counter. Returns the new value."""
        self._counters[name] += value
        return self._counters[name]

    async def gauge_set(self, name: str, value: float) -> None:
        """Set a gauge to a specific value."""
        self._gauges[name] = value

    async def gauge_add(self, name: str, delta: float) -> float:
        """Add to a gauge. Returns the new value."""
        self._gauges[name] = self._gauges.get(name, 0.0) + delta
        return self._gauges[name]

    async def record_timing(self, name: str, seconds: float) -> None:
        """Record a timing in seconds (converted to ms for storage)."""
        hist = self._histograms[name]
        hist.append(seconds * 1000)
        if len(hist) > self._max_histogram_size:
            self._histograms[name] = hist[-self._max_histogram_size:]

    async def snapshot(self) -> dict[str, Any]:
        """Take a snapshot of all current metrics."""
        result: dict[str, Any] = {}
        for name, value in self._counters.items():
            result[f"counter.{name}"] = value
        for name, value in self._gauges.items():
            result[f"gauge.{name}"] = value
        for name, values in self._histograms.items():
            if values:
                result[f"histogram.{name}"] = {
                    "count": len(values),
                    "min": round(min(values), 2),
                    "max": round(max(values), 2),
                    "avg": round(sum(values) / len(values), 2),
                    "p50": self._percentile(values, 50),
                    "p95": self._percentile(values, 95),
                    "p99": self._percentile(values, 99),
                }
        result["timestamp"] = time.time()
        return result

    def _percentile(self, values: list[float], p: int) -> float:
        """Calculate the p-th percentile of a sorted list."""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        k = (len(sorted_vals) - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < len(sorted_vals) else f
        return round(sorted_vals[f] * (c - k) + sorted_vals[c] * (k - f), 2)

    def get(self, name: str, default: Any = 0) -> int:
        """Get a counter value."""
        return self._counters.get(name, default)

    def reset(self) -> None:
        """Reset all metrics."""
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
