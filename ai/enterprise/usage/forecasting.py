"""Usage forecasting."""

from __future__ import annotations


class UsageForecasting:
    def __init__(self) -> None:
        self._history: dict[str, dict[str, list[float]]] = {}

    def record(self, org_id: str, metric: str, value: float) -> None:
        self._history.setdefault(org_id, {}).setdefault(metric, []).append(value)
        if len(self._history[org_id][metric]) > 100:
            self._history[org_id][metric] = self._history[org_id][metric][-100:]

    def forecast(self, org_id: str, metric: str, periods: int = 5) -> list[float]:
        values = self._history.get(org_id, {}).get(metric, [])
        if len(values) < 3:
            return [0.0] * periods
        avg_growth = (values[-1] - values[0]) / max(len(values) - 1, 1)
        last = values[-1]
        return [last + avg_growth * (i + 1) for i in range(periods)]

    def predict_next(self, org_id: str, metric: str) -> float:
        forecast = self.forecast(org_id, metric, 1)
        return forecast[0] if forecast else 0.0

    def will_exceed(self, org_id: str, metric: str, limit: float, periods: int = 5) -> bool:
        forecast = self.forecast(org_id, metric, periods)
        return any(v > limit for v in forecast)

    def list_metrics(self, org_id: str) -> list[str]:
        return list(self._history.get(org_id, {}).keys())

    def get_history(self, org_id: str, metric: str) -> list[float]:
        return list(self._history.get(org_id, {}).get(metric, []))
