from __future__ import annotations

from typing import Any

from ..monitoring_models import MetricSample, MetricType


class CacheMetrics:
    """Cache hit/miss ratio and latency metrics."""

    def __init__(self) -> None:
        self._hits: int = 0
        self._misses: int = 0
        self._total_ops: int = 0

    def record_hit(self) -> MetricSample:
        self._hits += 1
        self._total_ops += 1
        return MetricSample("cache_hits_total", 1.0, metric_type=MetricType.COUNTER)

    def record_miss(self) -> MetricSample:
        self._misses += 1
        self._total_ops += 1
        return MetricSample("cache_misses_total", 1.0, metric_type=MetricType.COUNTER)

    @property
    def hit_ratio(self) -> float:
        if self._total_ops == 0:
            return 0.0
        return self._hits / self._total_ops

    def snapshot(self) -> dict[str, Any]:
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total_ops": self._total_ops,
            "hit_ratio": round(self.hit_ratio, 4),
        }

    def reset(self) -> None:
        self._hits = 0
        self._misses = 0
        self._total_ops = 0


__all__ = ["CacheMetrics"]
