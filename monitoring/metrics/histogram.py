from __future__ import annotations

from typing import Any

from ..monitoring_models import MetricSample, MetricType


class Histogram:
    """Samples observations and computes quantiles."""

    def __init__(self, name: str, labels: dict[str, str] | None = None, buckets: list[float] | None = None) -> None:
        self._name = name
        self._labels = labels or {}
        self._buckets = sorted(buckets) if buckets else [0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
        self._values: list[float] = []

    def observe(self, value: float) -> MetricSample:
        self._values.append(value)
        return MetricSample(
            name=self._name, value=value,
            labels=self._labels, metric_type=MetricType.HISTOGRAM,
        )

    def stats(self) -> dict[str, float]:
        if not self._values:
            return {"count": 0, "sum": 0.0, "avg": 0.0, "min": 0.0, "max": 0.0}
        return {
            "count": len(self._values),
            "sum": sum(self._values),
            "avg": sum(self._values) / len(self._values),
            "min": min(self._values),
            "max": max(self._values),
        }

    def percentile(self, p: float) -> float:
        if not self._values:
            return 0.0
        sorted_vals = sorted(self._values)
        idx = max(0, min(len(sorted_vals) - 1, int(len(sorted_vals) * p / 100)))
        return sorted_vals[idx]

    def reset(self) -> None:
        self._values.clear()


__all__ = ["Histogram"]
