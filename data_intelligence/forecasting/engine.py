"""Forecasting engine (attached by the facade as ``forecasting``).

Stores historical series (sales, weather, dates, region, promotions) and
produces point forecasts with naive, seasonal, moving average, exponential
and seasonal-factor methods.
"""

from __future__ import annotations

from typing import Any

from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.forecasting.base import (ForecastError, Forecaster)
from data_intelligence.forecasting.exponential import (
    ExponentialSmoothingForecaster)
from data_intelligence.forecasting.moving_average import (
    MovingAverageForecaster)
from data_intelligence.forecasting.naive import (NaiveForecaster,
                                                 SeasonalNaiveForecaster)
from data_intelligence.forecasting.seasonal import SeasonalForecaster

METHODS = ("naive", "seasonal_naive", "moving_average", "exponential",
           "seasonal")


class ForecastingEngine:
    """Coordinates historical series, forecasts and backtesting."""

    def __init__(self, metrics: DataIntelligenceMetrics, config: Any,
                 context: Any) -> None:
        self._log = get_logger()
        self.metrics = metrics
        self.config = config
        self.context = context
        self.series: dict[str, list[dict[str, Any]]] = {}
        self.errors: dict[str, dict[str, float]] = {}

    def store_series(self, series_id: str,
                     points: list[dict[str, Any]]) -> int:
        """Stores labelled points (``period`` + ``value`` required)."""
        if not points:
            raise ForecastError("cannot store an empty series")
        for point in points:
            if "period" not in point or "value" not in point:
                raise ForecastError(
                    "each point needs 'period' and 'value' keys")
        self.series[series_id] = list(points)
        self.metrics.increment("forecasting.series")
        return len(points)

    def forecast(self, series_id: str, method: str = "naive",
                 horizon: int = 1, period: str | None = None,
                 **params: Any) -> dict[str, Any]:
        """Forecasts the next ``horizon`` values of the series."""
        points = self.series.get(series_id)
        if points is None:
            raise ForecastError(f"unknown series: {series_id}")
        if horizon < 1:
            raise ForecastError("horizon must be >= 1")
        forecaster = _build_forecaster(method, params)
        if method == "seasonal":
            forecaster.fit([(point["period"], point["value"])
                            for point in points])
            values = forecaster.forecast(horizon, period_key=period)
        else:
            forecaster.fit([float(point["value"]) for point in points])
            values = forecaster.forecast(horizon)
        error = self.errors.get(series_id)
        confidence = (max(0.0, 1.0 - error["mape"] / 100.0)
                      if error else 0.0)
        self.metrics.increment("forecasting.forecasts")
        return {"series_id": series_id, "method": method,
                "horizon": horizon, "period": period,
                "forecast": values, "confidence": confidence}

    def evaluate(self, series_id: str, method: str = "naive",
                 train_ratio: float = 0.8,
                 **params: Any) -> dict[str, Any]:
        """Backtests a method and stores MAE/MAPE for confidence."""
        points = self.series.get(series_id)
        if points is None:
            raise ForecastError(f"unknown series: {series_id}")
        if not 0.0 < train_ratio < 1.0:
            raise ForecastError("train_ratio must be between 0 and 1")
        split = max(1, int(len(points) * train_ratio))
        train, test = points[:split], points[split:]
        if not test:
            raise ForecastError("not enough points to evaluate")
        forecaster = _build_forecaster(method, params)
        if method == "seasonal":
            forecaster.fit([(point["period"], point["value"])
                            for point in train])
            predicted = [forecaster.forecast(1, period_key=point["period"])[0]
                         for point in test]
        else:
            forecaster.fit([float(point["value"]) for point in train])
            predicted = forecaster.forecast(len(test))
        actual = [float(point["value"]) for point in test]
        errors = [expected - got for expected, got in zip(actual, predicted)]
        mae = sum(abs(error) for error in errors) / len(errors)
        non_zero = [expected for expected, error in zip(actual, errors)
                    if expected != 0]
        mape = (sum(abs(error) / expected
                    for expected, error in zip(actual, errors)
                    if expected != 0) / len(non_zero) * 100
                if non_zero else 0.0)
        self.errors[series_id] = {"mae": mae, "mape": mape}
        self.metrics.increment("forecasting.evaluations")
        return {"series_id": series_id, "method": method, "mae": mae,
                "mape": mape, "n": len(test)}

    def stats(self) -> dict[str, Any]:
        return {"series": sorted(self.series),
                "methods": list(METHODS),
                "evaluated": sorted(self.errors)}


def _build_forecaster(method: str, params: dict[str, Any]) -> Any:
    if method == "naive":
        return NaiveForecaster()
    if method == "seasonal_naive":
        return SeasonalNaiveForecaster(season=int(params.get("season", 12)))
    if method == "moving_average":
        return MovingAverageForecaster(
            window=int(params.get("window", 3)))
    if method == "exponential":
        return ExponentialSmoothingForecaster(
            alpha=float(params.get("alpha", 0.3)))
    if method == "seasonal":
        return SeasonalForecaster()
    raise ForecastError(f"unknown method: {method}")
