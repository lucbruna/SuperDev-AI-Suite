"""Prescriptive analytics: what should we do."""

from __future__ import annotations

from typing import Any

from data_intelligence.analytics.base import AnalyticsError, AnalyticsProvider
from data_intelligence.data_models import AnalyticsLevel


class PrescriptiveAnalytics(AnalyticsProvider):
    """Recommends actions based on rules and targets.

    Metrics:
        * ``recommend``  - applies the configured rules over the input data.
        * ``gap_to_target`` - by how much (percentage) the current value must
          move to reach the target, plus a suggested adjustment.
    """

    level = AnalyticsLevel.PRESCRIPTIVE

    def __init__(self, rules: list[dict[str, Any]] | None = None) -> None:
        # Each rule: {"name", "field", "op" ("lt"/"gt"/"lte"/"gte"), "value",
        #             "recommendation"}
        self.rules = rules or []

    def compute(self, metric: str,
                data: list[dict[str, Any]]) -> dict[str, Any]:
        if metric == "recommend":
            return self._recommend(data)
        if metric == "gap_to_target":
            return self._gap(data)
        raise AnalyticsError(f"unknown prescriptive metric: {metric}")

    def _recommend(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        recommendations: list[dict[str, Any]] = []
        for rule in self.rules:
            field = rule.get("field")
            if not isinstance(field, str):
                continue
            op = str(rule.get("op", "lt"))
            threshold = rule.get("value")
            if threshold is None:
                continue
            try:
                threshold_float = float(threshold)
            except (TypeError, ValueError):
                continue
            for record in data:
                value = record.get(field)
                if value is None:
                    continue
                try:
                    value_float = float(value)
                except (TypeError, ValueError):
                    continue
                matched = value_float < threshold_float if op == "lt" \
                    else value_float > threshold_float if op == "gt" \
                    else value_float <= threshold_float if op == "lte" \
                    else value_float >= threshold_float
                if matched:
                    recommendations.append({
                        "rule": str(rule.get("name", "unnamed")),
                        "field": field, "value": value,
                        "threshold": threshold,
                        "recommendation": str(
                            rule.get("recommendation", "")),
                    })
        return {"metric": "recommend", "value": recommendations,
                "detail": {"rules_checked": len(self.rules)}}

    def _gap(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        current = self._first_float(data, "current")
        target = self._first_float(data, "target")
        if current == 0:
            raise AnalyticsError("current must be non-zero")
        gap = round((current - target) / abs(current) * 100, 2)
        return {"metric": "gap_to_target", "value": gap,
                "detail": {"current": current, "target": target,
                           "adjustment": f"{'reduce' if gap > 0 else 'increase'} "
                                         f"by {abs(gap)}%"}}

    @staticmethod
    def _first_float(data: list[dict[str, Any]], field: str) -> float:
        for record in data:
            if field in record:
                return float(record[field])
        raise AnalyticsError(f"missing field: {field}")
