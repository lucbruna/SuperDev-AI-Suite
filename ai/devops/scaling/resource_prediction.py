"""Resource prediction."""

from __future__ import annotations

from typing import Any


class ResourcePredictor:
    def __init__(self) -> None:
        self._predictions: list[dict[str, Any]] = []

    def predict(self, resource: str, history: list[float], horizon: int = 24) -> dict[str, Any]:
        if not history:
            return {"error": "no_data"}
        avg = sum(history) / len(history)
        trend = (history[-1] - history[0]) / max(len(history) - 1, 1)
        predictions = [avg + trend * (i + 1) for i in range(horizon)]
        result = {"resource": resource, "predictions": predictions, "trend": trend, "horizon": horizon}
        self._predictions.append(result)
        return result

    def get_predictions(self, resource: str = "", limit: int = 20) -> list[dict[str, Any]]:
        preds = self._predictions
        if resource:
            preds = [p for p in preds if p.get("resource") == resource]
        return preds[-limit:]

    def count(self) -> int:
        return len(self._predictions)
