"""Business forecasting."""

from __future__ import annotations


class BusinessForecasting:
    def __init__(self) -> None:
        self._data: dict[str, list[float]] = {}

    def record(self, metric: str, value: float) -> None:
        self._data.setdefault(metric, []).append(value)
        if len(self._data[metric]) > 100:
            self._data[metric] = self._data[metric][-100:]

    def forecast(self, metric: str, periods: int = 5) -> list[float]:
        values = self._data.get(metric, [])
        if len(values) < 3:
            return [0.0] * periods
        avg_growth = (values[-1] - values[0]) / max(len(values) - 1, 1)
        last = values[-1]
        return [last + avg_growth * (i + 1) for i in range(periods)]

    def predict_next(self, metric: str) -> float:
        forecast = self.forecast(metric, 1)
        return forecast[0] if forecast else 0.0

    def get_growth_rate(self, metric: str) -> float:
        values = self._data.get(metric, [])
        if len(values) < 2:
            return 0.0
        return (values[-1] - values[0]) / max(abs(values[0]), 1) * 100

    def list_metrics(self) -> list[str]:
        return list(self._data.keys())

    def get_values(self, metric: str) -> list[float]:
        return list(self._data.get(metric, []))

    def clear(self, metric: str = "") -> int:
        if metric:
            n = len(self._data.get(metric, []))
            self._data.pop(metric, None)
            return n
        n = sum(len(v) for v in self._data.values())
        self._data.clear()
        return n
