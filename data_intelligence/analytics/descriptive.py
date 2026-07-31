"""Descriptive analytics: what happened."""

from __future__ import annotations

from typing import Any

from data_intelligence.analytics.base import AnalyticsError, AnalyticsProvider
from data_intelligence.analytics.metrics import average, growth_rate, total
from data_intelligence.data_models import AnalyticsLevel
from data_intelligence.data_protocols import numeric_values


class DescriptiveAnalytics(AnalyticsProvider):
    """Summarizes the past: totals, averages and growth.

    Metrics:
        * ``total``         - sum of ``value_field``.
        * ``average``       - mean of ``value_field``.
        * ``growth``        - growth between ``previous_period`` records and
          ``current_period`` records (returns a percentage).
        * ``distribution``  - sum grouped by ``group_by``.
    """

    level = AnalyticsLevel.DESCRIPTIVE

    def __init__(self, value_field: str = "value",
                 group_by: str = "group") -> None:
        self.value_field = value_field
        self.group_by = group_by

    def compute(self, metric: str,
                data: list[dict[str, Any]]) -> dict[str, Any]:
        if metric == "total":
            return {"metric": metric, "value": total(
                numeric_values(data, self.value_field))}
        if metric == "average":
            return {"metric": metric, "value": average(
                numeric_values(data, self.value_field))}
        if metric == "growth":
            return self._growth(data)
        if metric == "distribution":
            return self._distribution(data)
        raise AnalyticsError(f"unknown descriptive metric: {metric}")

    def _growth(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        periods = [r for r in data if "period" in r]
        if not periods:
            raise AnalyticsError(
                "growth requires records with a 'period' field")
        buckets: dict[str, float] = {}
        for record in periods:
            period = str(record["period"])
            buckets[period] = buckets.get(period, 0.0) + float(
                record.get(self.value_field, 0))
        periods_sorted = sorted(buckets)
        if len(periods_sorted) < 2:
            raise AnalyticsError("growth requires at least two periods")
        latest = periods_sorted[-1]
        previous = periods_sorted[-2]
        rate = growth_rate(buckets[latest], buckets[previous])
        return {"metric": "growth", "value": rate,
                "detail": {"latest": latest, "previous": previous,
                           "latest_value": buckets[latest],
                           "previous_value": buckets[previous]}}

    def _distribution(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        buckets: dict[str, float] = {}
        for record in data:
            key = str(record.get(self.group_by, "unknown"))
            buckets[key] = buckets.get(key, 0.0) + float(
                record.get(self.value_field, 0))
        return {"metric": "distribution", "value": buckets}
