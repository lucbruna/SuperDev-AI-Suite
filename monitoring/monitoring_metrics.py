from __future__ import annotations

import time
from typing import Any

from .monitoring_models import MetricSample, MetricType


class MonitoringMetrics:
    """In-memory metrics store supporting counter, gauge, histogram, summary, timer."""

    def __init__(self) -> None:
        self._counters: dict[str, float] = {}
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = {}
        self._samples: list[MetricSample] = []

    def increment(self, name: str, value: float = 1.0, labels: dict[str, str] | None = None) -> None:
        key = self._metric_key(name, labels)
        self._counters[key] = self._counters.get(key, 0.0) + value
        self._samples.append(MetricSample(
            name=name, value=self._counters[key],
            labels=labels or {}, metric_type=MetricType.COUNTER,
        ))

    def gauge(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        key = self._metric_key(name, labels)
        self._gauges[key] = value
        self._samples.append(MetricSample(
            name=name, value=value, labels=labels or {}, metric_type=MetricType.GAUGE,
        ))

    def observe(self, name: str, value: float, labels: dict[str, str] | None = None) -> None:
        key = self._metric_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = []
        self._histograms[key].append(value)
        self._samples.append(MetricSample(
            name=name, value=value, labels=labels or {}, metric_type=MetricType.HISTOGRAM,
        ))

    def timer(self, name: str, labels: dict[str, str] | None = None) -> _Timer:
        return _Timer(self, name, labels or {})

    def get_snapshot(self) -> list[MetricSample]:
        return list(self._samples)

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

    def reset(self) -> None:
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()
        self._samples.clear()

    @staticmethod
    def _metric_key(name: str, labels: dict[str, str] | None = None) -> str:
        if labels:
            parts = [f"{k}={v}" for k, v in sorted(labels.items())]
            return f"{name}{{{','.join(parts)}}}"
        return name


class _Timer:
    """Context manager for timing metric observations."""

    def __init__(self, metrics: MonitoringMetrics, name: str, labels: dict[str, str]) -> None:
        self._metrics = metrics
        self._name = name
        self._labels = labels
        self._start: float = 0.0

    def __enter__(self) -> _Timer:
        self._start = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        elapsed = (time.perf_counter() - self._start) * 1000
        self._metrics.observe(self._name, elapsed, self._labels)


__all__ = ["MonitoringMetrics"]
