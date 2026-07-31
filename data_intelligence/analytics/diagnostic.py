"""Diagnostic analytics: why it happened."""

from __future__ import annotations

from typing import Any

from data_intelligence.analytics.base import AnalyticsError, AnalyticsProvider
from data_intelligence.analytics.metrics import average, total
from data_intelligence.data_models import AnalyticsLevel
from data_intelligence.data_protocols import numeric_values


class DiagnosticAnalytics(AnalyticsProvider):
    """Investigates causes: group comparison and anomalies.

    Metrics:
        * ``compare``   - compares totals/averages across groups (``group_by``)
          and highlights the largest difference.
        * ``anomalies`` - flags records whose ``value_field`` deviates more
          than ``std_dev_factor`` standard deviations from the mean.
    """

    level = AnalyticsLevel.DIAGNOSTIC

    def __init__(self, value_field: str = "value",
                 group_by: str = "group") -> None:
        self.value_field = value_field
        self.group_by = group_by

    def compute(self, metric: str,
                data: list[dict[str, Any]]) -> dict[str, Any]:
        if metric == "compare":
            return self._compare(data)
        if metric == "anomalies":
            return self._anomalies(data)
        raise AnalyticsError(f"unknown diagnostic metric: {metric}")

    def _compare(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        buckets: dict[str, float] = {}
        counts: dict[str, int] = {}
        for record in data:
            key = str(record.get(self.group_by, "unknown"))
            buckets[key] = buckets.get(key, 0.0) + float(
                record.get(self.value_field, 0))
            counts[key] = counts.get(key, 0) + 1
        if not buckets:
            raise AnalyticsError("no records to compare")
        groups = sorted(buckets, key=lambda k: buckets[k])
        best, worst = groups[-1], groups[0]
        return {"metric": "compare",
                "value": {k: buckets[k] for k in groups},
                "detail": {"best": best, "worst": worst,
                           "gap": round(buckets[best] - buckets[worst], 4),
                           "gap_percent": self._gap_percent(buckets[best],
                                                            buckets[worst])}}

    @staticmethod
    def _gap_percent(best: float, worst: float) -> float:
        if worst == 0:
            return 100.0
        return round((best - worst) / worst * 100, 2)

    def _anomalies(self, data: list[dict[str, Any]],
                   std_dev_factor: float = 2.0) -> dict[str, Any]:
        import statistics

        values = numeric_values(data, self.value_field)
        if len(values) < 2:
            return {"metric": "anomalies", "value": [], "detail": {
                "mean": average(values)}}
        mean = average(values)
        stdev = statistics.pstdev(values) if len(values) > 1 else 0.0
        anomalies: list[dict[str, Any]] = []
        for record in data:
            value = float(record.get(self.value_field, 0))
            if stdev and abs(value - mean) > std_dev_factor * stdev:
                anomalies.append({"index": len(anomalies),
                                  "value": value, "record": record})
        return {"metric": "anomalies", "value": anomalies,
                "detail": {"mean": mean, "std_dev": round(stdev, 4)}}
