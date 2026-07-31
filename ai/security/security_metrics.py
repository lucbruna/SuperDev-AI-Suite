"""Security metrics collector."""
from __future__ import annotations

from typing import Any


class SecurityMetrics:
    """Collects and aggregates security-related metrics."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._timers: dict[str, list[float]] = {}
        self._gauge_values: dict[str, float] = {}

    def increment(self, name: str, value: int = 1) -> None:
        self._counters[name] = self._counters.get(name, 0) + value

    def record_time(self, name: str, duration_ms: float) -> None:
        self._timers.setdefault(name, []).append(duration_ms)

    def set_gauge(self, name: str, value: float) -> None:
        self._gauge_values[name] = value

    def get_counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    def get_timer_stats(self, name: str) -> dict[str, float]:
        values = self._timers.get(name, [])
        if not values:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}
        return {
            "count": len(values),
            "avg": round(sum(values) / len(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
        }

    def get_gauge(self, name: str) -> float:
        return self._gauge_values.get(name, 0.0)

    def get_all(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauge_values),
            "timers": {k: self.get_timer_stats(k) for k in self._timers},
        }

    def reset(self) -> None:
        self._counters.clear()
        self._timers.clear()
        self._gauge_values.clear()
