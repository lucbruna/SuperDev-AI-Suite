"""Trend analytics — detects trends in production data."""
from __future__ import annotations

from typing import Any


class TrendAnalytics:
    """Detects upward/downward trends from a metric series."""

    def detect(self, series: list[float]) -> dict[str, Any]:
        if len(series) < 2:
            return {"trend": "insufficient_data", "delta": 0.0}
        delta = series[-1] - series[0]
        trend = "up" if delta > 0 else "down" if delta < 0 else "flat"
        return {"trend": trend, "delta": round(delta, 3)}


_trend_analytics: TrendAnalytics | None = None


def get_trend_analytics() -> TrendAnalytics:
    global _trend_analytics
    if _trend_analytics is None:
        _trend_analytics = TrendAnalytics()
    return _trend_analytics
