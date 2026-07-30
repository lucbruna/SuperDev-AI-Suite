from __future__ import annotations

from typing import Any

from ..monitoring_models import MetricSample, MetricType


class VectorMetrics:
    """Metrics for vector database operations."""

    def __init__(self) -> None:
        self._searches: int = 0
        self._indexed_vectors: int = 0

    def record_search(self, duration_ms: float, result_count: int = 0) -> list[MetricSample]:
        self._searches += 1
        return [
            MetricSample("vector_searches_total", 1.0, metric_type=MetricType.COUNTER),
            MetricSample("vector_search_duration_ms", duration_ms, metric_type=MetricType.HISTOGRAM),
            MetricSample("vector_search_results", float(result_count), metric_type=MetricType.GAUGE),
        ]

    def record_index(self, count: int = 1) -> MetricSample:
        self._indexed_vectors += count
        return MetricSample("vector_indexed_total", float(count), metric_type=MetricType.COUNTER)

    def snapshot(self) -> dict[str, Any]:
        return {
            "searches": self._searches,
            "indexed_vectors": self._indexed_vectors,
        }


__all__ = ["VectorMetrics"]
