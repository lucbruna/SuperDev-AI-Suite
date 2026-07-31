"""Forecasting."""
from __future__ import annotations
from typing import Any, Dict, List

class Forecaster:
    def __init__(self) -> None:
        self._forecasts: List[Dict[str, Any]] = []
    def forecast(self, historical_data: List[float], horizon: int = 10, method: str = "linear") -> Dict[str, Any]:
        if not historical_data:
            return {"error": "no_data"}
        last = historical_data[-1]
        trend = (historical_data[-1] - historical_data[0]) / max(len(historical_data) - 1, 1)
        predictions = [last + trend * (i + 1) for i in range(horizon)]
        forecast = {"horizon": horizon, "method": method, "predictions": predictions, "trend": trend}
        self._forecasts.append(forecast)
        return forecast
    def moving_average(self, data: List[float], window: int = 5) -> List[float]:
        result = []
        for i in range(len(data)):
            start = max(0, i - window + 1)
            result.append(sum(data[start:i+1]) / (i - start + 1))
        return result
    def exponential_smoothing(self, data: List[float], alpha: float = 0.3, horizon: int = 5) -> List[float]:
        if not data:
            return []
        smoothed = [data[0]]
        for i in range(1, len(data)):
            smoothed.append(alpha * data[i] + (1 - alpha) * smoothed[-1])
        last = smoothed[-1]
        return [last] * horizon
    def get_forecasts(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._forecasts[-limit:]
    def count(self) -> int:
        return len(self._forecasts)
