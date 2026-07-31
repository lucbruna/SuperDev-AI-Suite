from __future__ import annotations

import time
from typing import Any

from .data_models import DataQualityStatus, DataRecord


class DataMetrics:
    """In-memory metrics store for data operations: counters, gauges, histograms, timers."""

    def __init__(self) -> None:
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
        self._quality_counts: dict[DataQualityStatus, int] = {
            DataQualityStatus.UNKNOWN: 0,
            DataQualityStatus.GOOD: 0,
            DataQualityStatus.WARNING: 0,
            DataQualityStatus.BAD: 0,
        }

    def increment(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        key = self._metric_key(name, labels)
        self._counters[key] = self._counters.get(key, 0.0) + value

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        self._gauges[self._metric_key(name, labels)] = value

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        key = self._metric_key(name, labels)
        self._histograms.setdefault(key, []).append(value)

    def timer(self, name: str, labels: dict[str, str] | None = None) -> _DataTimer:
        return _DataTimer(self, name, labels or {})

    def record_record(self, record: DataRecord) -> None:
        self.increment("records.total")
        self._quality_counts[record.quality] = self._quality_counts.get(record.quality, 0) + 1

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

    def quality_distribution(self) -> dict[str, int]:
        return {k.value: v for k, v in self._quality_counts.items()}

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {
                k: {"count": len(v), "sum": sum(v), "avg": sum(v) / len(v) if v else 0.0}
                for k, v in self._histograms.items()
            },
            "quality": self.quality_distribution(),
        }

    def reset(self) -> None:
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._quality_counts = {
            DataQualityStatus.UNKNOWN: 0,
            DataQualityStatus.GOOD: 0,
            DataQualityStatus.WARNING: 0,
            DataQualityStatus.BAD: 0,
        }

    @staticmethod
    def _metric_key(name: str, labels: dict[str, str] | None = None) -> str:
        if labels:
            parts = [f"{k}={v}" for k, v in sorted(labels.items())]
            return f"{name}{{{','.join(parts)}}}"
        return name


class _DataTimer:
    """Context manager for timing metric observations."""

    def __init__(self, metrics: DataMetrics, name: str, labels: dict[str, str]) -> None:
        self._metrics = metrics
        self._name = name
        self._labels = labels
        self._start: float = 0.0

    def __enter__(self) -> _DataTimer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        elapsed = (time.perf_counter() - self._start) * 1000
        self._metrics.observe(self._name, elapsed, self._labels)


__all__ = ["DataMetrics"]
