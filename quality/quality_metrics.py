from __future__ import annotations

import time
from typing import Any


class QualityMetrics:
    """In-memory metrics store for quality operations: counters, gauges, histograms."""

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

    def timer(self, name: str, labels: dict[str, str] | None = None) -> _QualityTimer:
        return _QualityTimer(self, name, labels or {})

    def get_counter(self, name: str, labels: dict[str, str] | None = None) -> float:
        return self._counters.get(self._metric_key(name, labels), 0.0)

    def get_gauge(self, name: str, labels: dict[str, str] | None = None) -> float | None:
        return self._gauges.get(self._metric_key(name, labels))

    def get_histogram(self, name: str, labels: dict[str, str] | None = None) -> dict[str, float]:
        values = self._histograms.get(self._metric_key(name, labels), [])
        if not values:
            return {"count": 0, "sum": 0.0, "avg": 0.0, "min": 0.0, "max": 0.0}
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                k: {"count": len(v), "sum": sum(v), "avg": sum(v) / len(v) if v else 0.0}
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


class _QualityTimer:
    """Context manager for timing metric observations."""

    def __init__(self, metrics: QualityMetrics, name: str, labels: dict[str, str]) -> None:
        self._metrics = metrics
        self._name = name
        self._labels = labels
        self._start: float = 0.0

    def __enter__(self) -> _QualityTimer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        elapsed = (time.perf_counter() - self._start) * 1000
        self._metrics.observe(self._name, elapsed, self._labels)


__all__ = ["QualityMetrics"]
