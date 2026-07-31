"""Failure prediction."""
from __future__ import annotations
from typing import Any, Dict, List

class FailurePredictor:
    def __init__(self) -> None:
        self._predictions: List[Dict[str, Any]] = []
    def predict(self, component: str, sensor_data: Dict[str, float], thresholds: Dict[str, float] = None) -> Dict[str, Any]:
        thresholds = thresholds or {"temperature": 80.0, "vibration": 5.0, "wear": 0.8}
        alerts = []
        for sensor, value in sensor_data.items():
            threshold = thresholds.get(sensor, value * 1.5)
            if value > threshold:
                alerts.append({"sensor": sensor, "value": value, "threshold": threshold, "severity": "high"})
            elif value > threshold * 0.8:
                alerts.append({"sensor": sensor, "value": value, "threshold": threshold, "severity": "medium"})
        failure_prob = min(1.0, len(alerts) * 0.2)
        result = {"component": component, "alerts": alerts, "failure_probability": failure_prob, "estimated_time_hours": max(1, int(100 - failure_prob * 80))}
        self._predictions.append(result)
        return result
    def get_predictions(self, component: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        preds = self._predictions
        if component:
            preds = [p for p in preds if p.get("component") == component]
        return preds[-limit:]
    def count(self) -> int:
        return len(self._predictions)
    def high_risk_components(self, threshold: float = 0.5) -> List[Dict[str, Any]]:
        return [p for p in self._predictions if p.get("failure_probability", 0) >= threshold]
