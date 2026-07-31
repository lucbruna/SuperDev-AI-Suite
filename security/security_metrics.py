"""Metrics store for the Security Engine (Volume 16)."""

from __future__ import annotations

from typing import Any


class SecurityMetrics:
    """In-memory metrics: counters, gauges, histograms."""

    def __init__(self) -> None:
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}

    def increment(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        key = self._metric_key(name, labels)
        self._counters[key] = self._counters.get(key, 0.0) + value

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self._gauges[self._metric_key(name, labels)] = value

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        key = self._metric_key(name, labels)
        self._histograms.setdefault(key, []).append(value)

    def get_counter(self, name: str, labels: dict[str, str] | None = None) -> float:
        return self._counters.get(self._metric_key(name, labels), 0.0)

    def get_gauge(self, name: str, labels: dict[str, str] | None = None) -> float | None:
        return self._gauges.get(self._metric_key(name, labels))

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                k: {
                    "count": len(v),
                    "sum": sum(v),
                    "avg": sum(v) / len(v) if v else 0.0,
                }
                for k, v in self._histograms.items()
            },
        }

    def reset(self) -> None:
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()

    @staticmethod
    def _metric_key(name: str, labels: dict[str, str] | None = None) -> str:
        if labels:
            parts = [f"{k}={v}" for k, v in sorted(labels.items())]
            return f"{name}{{{','.join(parts)}}}"
        return name
