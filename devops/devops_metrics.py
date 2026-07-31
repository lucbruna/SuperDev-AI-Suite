from __future__ import annotations

from typing import Any


class DevOpsMetrics:
    """Metrics collector for DevOps operations."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}

    def increment(self, metric: str, value: int = 1) -> None:
        self._counters[metric] = self._counters.get(metric, 0) + value

    def gauge(self, metric: str, value: float) -> None:
        self._gauges[metric] = value

    def observe(self, metric: str, value: float) -> None:
        self._histograms.setdefault(metric, []).append(value)

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
        }

    def reset(self) -> None:
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
