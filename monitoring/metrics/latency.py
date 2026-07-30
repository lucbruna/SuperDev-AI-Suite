from __future__ import annotations

from ..monitoring_models import MetricSample, MetricType


class LatencyTracker:
    """Tracks latency percentiles for a specific operation."""

    def __init__(self, name: str, labels: dict[str, str] | None = None) -> None:
        self._name = name
        self._labels = labels or {}
        self._values: list[float] = []

    def record(self, ms: float) -> MetricSample:
        self._values.append(ms)
        return MetricSample(
            name=self._name, value=ms,
            labels=self._labels, metric_type=MetricType.HISTOGRAM,
        )

    def p50(self) -> float:
        return self._percentile(50)

    def p95(self) -> float:
        return self._percentile(95)

    def p99(self) -> float:
        return self._percentile(99)

    def avg(self) -> float:
        if not self._values:
            return 0.0
        return sum(self._values) / len(self._values)

    def _percentile(self, p: float) -> float:
        if not self._values:
            return 0.0
        sorted_vals = sorted(self._values)
        idx = max(0, min(len(sorted_vals) - 1, int(len(sorted_vals) * p / 100)))
        return sorted_vals[idx]


__all__ = ["LatencyTracker"]
