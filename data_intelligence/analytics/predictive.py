"""Predictive analytics: what will happen."""

from __future__ import annotations

from typing import Any

from data_intelligence.analytics.base import AnalyticsError, AnalyticsProvider
from data_intelligence.data_models import AnalyticsLevel
from data_intelligence.data_protocols import numeric_values


class PredictiveAnalytics(AnalyticsProvider):
    """Forecasts future values using simple methods.

    Metrics:
        * ``trend``         - linear least-squares forecast for the next
          ``horizon`` periods given records with ``period`` (numeric index)
          and ``value_field``.
        * ``days_until``    - days until ``inventory`` runs out given an
          ``daily_demand`` (e.g. ``estoque acaba em 12 dias``).
        * ``run_rate``      - projected total for the period based on
          elapsed fraction and current total.
    """

    level = AnalyticsLevel.PREDICTIVE

    def __init__(self, value_field: str = "value",
                 period_field: str = "period",
                 horizon: int = 1) -> None:
        self.value_field = value_field
        self.period_field = period_field
        self.horizon = horizon

    def compute(self, metric: str,
                data: list[dict[str, Any]]) -> dict[str, Any]:
        if metric == "trend":
            return self._trend(data)
        if metric == "days_until":
            return self._days_until(data)
        if metric == "run_rate":
            return self._run_rate(data)
        raise AnalyticsError(f"unknown predictive metric: {metric}")

    def _trend(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        points = [(float(r[self.period_field]),
                   float(r[self.value_field]))
                  for r in data
                  if self.period_field in r and self.value_field in r]
        if len(points) < 2:
            raise AnalyticsError("trend requires at least two points")
        slope, intercept = self._least_squares(points)
        last_period = int(max(p for p, _ in points))
        forecasts = {str(last_period + i): round(
            slope * (last_period + i) + intercept, 4)
            for i in range(1, self.horizon + 1)}
        return {"metric": "trend", "value": forecasts,
                "detail": {"slope": round(slope, 4),
                           "intercept": round(intercept, 4)}}

    def _days_until(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        inventory = self._first_float(data, "inventory")
        demand = self._first_float(data, "daily_demand")
        if demand <= 0:
            raise AnalyticsError("daily_demand must be positive")
        days = int(inventory // demand)
        return {"metric": "days_until", "value": days,
                "detail": {"inventory": inventory,
                           "daily_demand": demand}}

    def _run_rate(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        current = self._first_float(data, "current_total")
        fraction = self._first_float(data, "elapsed_fraction")
        if fraction <= 0:
            raise AnalyticsError("elapsed_fraction must be positive")
        projected = round(current / fraction, 4)
        return {"metric": "run_rate", "value": projected,
                "detail": {"current_total": current,
                           "elapsed_fraction": fraction}}

    @staticmethod
    def _least_squares(points: list[tuple[float, float]]) -> tuple[float, float]:
        n = len(points)
        sx = sum(p for p, _ in points)
        sy = sum(v for _, v in points)
        sxy = sum(p * v for p, v in points)
        sxx = sum(p * p for p, _ in points)
        denom = n * sxx - sx * sx
        if denom == 0:
            raise AnalyticsError("cannot fit a trend to constant periods")
        slope = (n * sxy - sx * sy) / denom
        intercept = (sy - slope * sx) / n
        return slope, intercept

    @staticmethod
    def _first_float(data: list[dict[str, Any]], field: str) -> float:
        for record in data:
            if field in record:
                return float(record[field])
        raise AnalyticsError(f"missing field: {field}")
