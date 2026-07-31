"""Outcome prediction."""
from __future__ import annotations
from typing import Any, Dict, List

class OutcomePredictor:
    def __init__(self) -> None:
        self._predictions: List[Dict[str, Any]] = []
    def predict(self, scenario: str, variables: Dict[str, Any], model: str = "default") -> Dict[str, Any]:
        outcomes = {}
        for key, value in variables.items():
            if isinstance(value, (int, float)):
                outcomes[key] = {"predicted": value * 1.1, "confidence": 0.75}
            else:
                outcomes[key] = {"predicted": value, "confidence": 0.8}
        overall_confidence = sum(o["confidence"] for o in outcomes.values()) / len(outcomes) if outcomes else 0
        result = {"scenario": scenario, "outcomes": outcomes, "overall_confidence": overall_confidence, "model": model}
        self._predictions.append(result)
        return result
    def sensitivity(self, base_prediction: Dict[str, Any], variable: str, range_vals: List[float]) -> Dict[str, Any]:
        sensitivities = []
        base_val = base_prediction.get("outcomes", {}).get(variable, {}).get("predicted", 0)
        for val in range_vals:
            change = val - base_val if base_val else 0
            sensitivities.append({"value": val, "change": change, "impact": change * 0.5})
        return {"variable": variable, "sensitivities": sensitivities}
    def get_predictions(self, scenario: str = "", limit: int = 20) -> List[Dict[str, Any]]:
        preds = self._predictions
        if scenario:
            preds = [p for p in preds if p.get("scenario") == scenario]
        return preds[-limit:]
    def count(self) -> int:
        return len(self._predictions)
