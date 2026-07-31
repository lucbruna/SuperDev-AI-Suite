"""Demand prediction."""

from __future__ import annotations

from typing import Any


class DemandPredictor:
    def __init__(self) -> None:
        self._predictions: list[dict[str, Any]] = []

    def predict(self, product: str, historical_sales: list[float], factors: dict[str, float] = None) -> dict[str, Any]:
        factors = factors or {"seasonality": 1.0, "trend": 1.0, "promotion": 1.0}
        base = historical_sales[-1] if historical_sales else 100
        predicted = base * factors.get("seasonality", 1.0) * factors.get("trend", 1.0) * factors.get("promotion", 1.0)
        result = {"product": product, "predicted_demand": predicted, "factors": factors, "base_demand": base}
        self._predictions.append(result)
        return result

    def seasonality_adjust(self, data: list[float], period: int = 12) -> list[float]:
        if len(data) < period:
            return data
        seasonal = []
        for i in range(len(data)):
            seasonal.append(data[i] / (sum(data[max(0, i - period + 1) : i + 1]) / min(period, i + 1)))
        return seasonal

    def get_predictions(self, product: str = "", limit: int = 20) -> list[dict[str, Any]]:
        preds = self._predictions
        if product:
            preds = [p for p in preds if p.get("product") == product]
        return preds[-limit:]

    def count(self) -> int:
        return len(self._predictions)
