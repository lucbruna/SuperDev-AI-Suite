from __future__ import annotations

from typing import Any

from ..monitoring_metrics import MonitoringMetrics


class MetricsEngine:
    """High-level metrics engine wrapping MonitoringMetrics with typed helpers."""

    def __init__(self) -> None:
        self._metrics = MonitoringMetrics()

    @property
    def metrics(self) -> MonitoringMetrics:
        return self._metrics

    def snapshot(self) -> list[Any]:
        return self._metrics.get_snapshot()

    def reset(self) -> None:
        self._metrics.reset()


__all__ = ["MetricsEngine"]
