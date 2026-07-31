"""Accuracy validation."""
from __future__ import annotations
from typing import Any, Dict, List

class AccuracyValidator:
    def __init__(self) -> None:
        self._validations: List[Dict[str, Any]] = []
    def validate(self, predictions: List[Any], expected: List[Any], tolerance: float = 0.01) -> Dict[str, Any]:
        correct = 0
        for pred, exp in zip(predictions, expected):
            if pred == exp:
                correct += 1
            elif isinstance(pred, (int, float)) and isinstance(exp, (int, float)):
                if abs(pred - exp) <= tolerance:
                    correct += 1
        total = len(expected)
        accuracy = (correct / total * 100) if total > 0 else 0
        result = {"accuracy": accuracy, "correct": correct, "total": total, "tolerance": tolerance}
        self._validations.append(result)
        return result
    def validate_distribution(self, data: List[float], expected_mean: float, expected_std: float, tolerance: float = 0.1) -> Dict[str, Any]:
        if not data:
            return {"error": "no_data"}
        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        std = variance ** 0.5
        mean_ok = abs(mean - expected_mean) <= tolerance
        std_ok = abs(std - expected_std) <= tolerance
        return {"mean": mean, "std": std, "expected_mean": expected_mean, "expected_std": expected_std, "mean_valid": mean_ok, "std_valid": std_ok, "valid": mean_ok and std_ok}
    def get_validations(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._validations[-limit:]
    def count(self) -> int:
        return len(self._validations)
