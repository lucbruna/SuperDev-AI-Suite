from __future__ import annotations

import time

from ..monitoring_models import MetricSample, MetricType


class ThroughputTracker:
    """Tracks operations per second over a window."""

    def __init__(self, name: str, labels: dict[str, str] | None = None) -> None:
        self._name = name
        self._labels = labels or {}
        self._count: int = 0
        self._window_start: float = time.time()

    def increment(self) -> None:
        self._count += 1

    def rate(self) -> MetricSample:
        elapsed = time.time() - self._window_start
        rps = self._count / elapsed if elapsed > 0 else 0.0
        self._count = 0
        self._window_start = time.time()
        return MetricSample(
            name=self._name, value=rps,
            labels=self._labels, metric_type=MetricType.GAUGE,
        )


__all__ = ["ThroughputTracker"]
