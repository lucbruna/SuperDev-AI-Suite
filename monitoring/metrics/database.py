from __future__ import annotations

from typing import Any

from ..monitoring_models import MetricSample, MetricType


class DatabaseMetrics:
    """Metrics collector for database engine performance."""

    def __init__(self) -> None:
        self._query_count: int = 0
        self._error_count: int = 0
        self._total_latency_ms: float = 0.0

    def record_query(self, duration_ms: float, success: bool = True) -> list[MetricSample]:
        self._query_count += 1
        self._total_latency_ms += duration_ms
        if not success:
            self._error_count += 1
        return [
            MetricSample("db_queries_total", 1.0, metric_type=MetricType.COUNTER),
            MetricSample("db_query_duration_ms", duration_ms, metric_type=MetricType.HISTOGRAM),
            MetricSample("db_errors_total", 0.0 if success else 1.0, metric_type=MetricType.COUNTER),
        ]

    def snapshot(self) -> dict[str, Any]:
        avg_latency = self._total_latency_ms / self._query_count if self._query_count > 0 else 0.0
        return {
            "query_count": self._query_count,
            "error_count": self._error_count,
            "avg_latency_ms": round(avg_latency, 2),
        }

    def reset(self) -> None:
        self._query_count = 0
        self._error_count = 0
        self._total_latency_ms = 0.0


__all__ = ["DatabaseMetrics"]
