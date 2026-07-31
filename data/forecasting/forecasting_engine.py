from __future__ import annotations

import statistics
from typing import Any

from ..data_models import AnomalyAlert, AnomalySeverity, ForecastResult
from .time_series import TimeSeriesAnalyzer


class ForecastingEngine:
    """Forecasting — time series, prediction, trends, anomalies, demand, risk."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.forecasting
        self._forecasts: dict[str, ForecastResult] = {}
        self._anomalies: list[AnomalyAlert] = []
        self._initialized = False
        # Deep-dive toolkit: engine.forecasting.time_series
        self.time_series = TimeSeriesAnalyzer(engine=self.engine)

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- moving average ------------------------------------------------------

    def _moving_average(self, series: list[float], horizon: int, window: int = 3) -> list[float]:
        if not series:
            return [0.0] * horizon
        last_values = series[-window:]
        step = sum(last_values) / len(last_values)
        return [round(step, 4)] * horizon

    # -- linear extrapolation ------------------------------------------------

    def _linear_trend(self, series: list[float], horizon: int) -> list[float]:
        if len(series) < 2:
            return self._moving_average(series, horizon)
        xs = list(range(len(series)))
        mx = statistics.mean(xs)
        my = statistics.mean(series)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, series, strict=False)) / max(
            sum((x - mx) ** 2 for x in xs), 1e-9
        )
        intercept = my - slope * mx
        return [round(intercept + slope * (len(series) + i), 4) for i in range(horizon)]

    async def forecast(
        self,
        series: list[float],
        horizon: int | None = None,
        method: str = "moving_average",
    ) -> ForecastResult:
        horizon = horizon or self.config.default_horizon
        values = self._linear_trend(series, horizon) if method == "linear" else self._moving_average(series, horizon)

        result = ForecastResult(
            series_name="series",
            horizon=horizon,
            values=values,
            confidence=self._confidence(series),
            method=method,
        )
        self._forecasts[result.forecast_id] = result
        self.engine.registry.register_forecast(result)
        self.engine.metrics.increment("forecasting.forecasts")
        return result

    def _confidence(self, series: list[float]) -> float:
        if len(series) < 2:
            return 0.5
        stdev = statistics.pstdev(series)
        mean = statistics.mean(series)
        volatility = stdev / mean if mean else 1.0
        return round(max(0.1, min(0.99, 1 - volatility)), 2)

    # -- trend analysis ------------------------------------------------------

    def trend_analysis(self, series: list[float]) -> dict[str, Any]:
        if not series:
            return {"trend": "empty", "delta": 0.0}
        delta = series[-1] - series[0]
        trend = "increasing" if delta > 0 else ("decreasing" if delta < 0 else "stable")
        return {"trend": trend, "delta": delta, "change_pct": round((delta / series[0] * 100), 2) if series[0] else 0.0}

    # -- anomaly detection ---------------------------------------------------

    def detect_anomalies(self, series: list[float], threshold: float | None = None) -> list[AnomalyAlert]:
        threshold = threshold or self.config.anomaly_threshold
        if len(series) < 3:
            return []
        mean = statistics.mean(series)
        stdev = statistics.pstdev(series)
        if stdev == 0:
            return []
        alerts: list[AnomalyAlert] = []
        for i, value in enumerate(series):
            z_score = abs((value - mean) / stdev)
            if z_score > threshold:
                severity = AnomalySeverity.HIGH if z_score > threshold * 2 else AnomalySeverity.MEDIUM
                alert = AnomalyAlert(
                    metric=f"series[{i}]",
                    severity=severity,
                    message=f"Value {value} deviates {z_score:.2f} sigma from mean",
                    context={"index": i, "z_score": round(z_score, 2)},
                )
                alerts.append(alert)
        self._anomalies.extend(alerts)
        return alerts

    # -- demand forecast -----------------------------------------------------

    async def demand_forecast(self, historical: list[float], horizon: int = 7) -> ForecastResult:
        return await self.forecast(historical, horizon=horizon, method="moving_average")

    # -- risk prediction -----------------------------------------------------

    def risk_score(self, series: list[float]) -> float:
        if len(series) < 2:
            return 0.0
        stdev = statistics.pstdev(series)
        mean = statistics.mean(series)
        return round(min(1.0, stdev / mean if mean else 1.0), 2)

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "forecasts": len(self._forecasts),
            "anomalies": len(self._anomalies),
        }


__all__ = ["ForecastingEngine"]
