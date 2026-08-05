"""Metrics Collector — counters, gauges and timers for studio ops."""
from __future__ import annotations

from typing import Any


class MetricsCollector:
    """Lightweight metrics store with snapshot support."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._timers: dict[str, list[float]] = {}

    def increment(self, name: str, value: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + value

    def timing(self, name: str, seconds: float) -> None:
        self._timers.setdefault(name, []).append(seconds)
        if len(self._timers[name]) > 1000:
            self._timers[name] = self._timers[name][-500:]

    def snapshot(self) -> dict[str, Any]:
        timers = {
            name: {"count": len(v), "avg_ms": round(sum(v) / len(v) * 1000, 2) if v else 0.0}
            for name, v in self._timers.items()
        }
        return {"counters": dict(self._counters), "timers": timers}


_metrics_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
