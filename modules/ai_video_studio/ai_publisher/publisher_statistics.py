"""Publisher Statistics — aggregates publish metrics across platforms (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class PublisherStatistics:
    """Accumulate and aggregate publish metrics."""

    def __init__(self) -> None:
        self._metrics: dict[str, dict] = {}

    def record(self, *, platform: str, metrics: dict) -> dict:
        """Merge metrics for a platform."""
        current = self._metrics.setdefault(platform.lower(), {})
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                current[key] = current.get(key, 0) + value
        return {"recorded": True, "platform": platform.lower()}

    def totals(self) -> dict:
        """Aggregate totals across all platforms."""
        totals: dict[str, float] = {}
        for platform_metrics in self._metrics.values():
            for key, value in platform_metrics.items():
                totals[key] = totals.get(key, 0) + value
        return totals

    def by_platform(self) -> dict[str, dict]:
        return {name: dict(m) for name, m in self._metrics.items()}

    def engagement_rate(self, *, platform: str | None = None) -> float:
        """Compute engagement rate (interactions / reach) for one or all platforms."""
        if platform:
            m = self._metrics.get(platform.lower(), {})
            interactions = m.get("likes", 0) + m.get("comments", 0) + m.get("shares", 0)
            reach = m.get("views", 0) or m.get("impressions", 0) or m.get("reach", 0)
        else:
            totals = self.totals()
            interactions = totals.get("likes", 0) + totals.get("comments", 0) + totals.get("shares", 0)
            reach = totals.get("views", 0) or totals.get("impressions", 0) or totals.get("reach", 0)
        if not reach:
            return 0.0
        return round(interactions / reach * 100.0, 2)

    def stats(self) -> dict[str, int]:
        return {"platforms": len(self._metrics)}


_STATISTICS: PublisherStatistics | None = None


def get_publisher_statistics() -> PublisherStatistics:
    """Get the module-level singleton statistics collector."""
    global _STATISTICS
    if _STATISTICS is None:
        _STATISTICS = PublisherStatistics()
    return _STATISTICS
