"""Forecasting."""
from __future__ import annotations

from typing import Any


class Forecaster:
    def __init__(self) -> None:
        self._forecasts: list[dict[str, Any]] = []
    def forecast(self, historical_data: list[float], horizon: int = 10, method: str = "linear") -> dict[str, Any]:
        if not historical_data:
            return {"error": "no_data"}
        last = historical_data[-1]
        trend = (historical_data[-1] - historical_data[0]) / max(len(historical_data) - 1, 1)
        predictions = [last + trend * (i + 1) for i in range(horizon)]
        forecast = {"horizon": horizon, "method": method, "predictions": predictions, "trend": trend}
        self._forecasts.append(forecast)
        return forecast
    def moving_average(self, data: list[float], window: int = 5) -> list[float]:
        result = []
        for i in range(len(data)):
            start = max(0, i - window + 1)
            result.append(sum(data[start:i+1]) / (i - start + 1))
        return result
    def exponential_smoothing(self, data: list[float], alpha: float = 0.3, horizon: int = 5) -> list[float]:
        if not data:
            return []
        smoothed = [data[0]]
        for i in range(1, len(data)):
            smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[-1])
        last = smoothed[-1]
        return [last] * horizon
    def get_forecasts(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._forecasts[-limit:]
    def count(self) -> int:
        return len(self._forecasts)
