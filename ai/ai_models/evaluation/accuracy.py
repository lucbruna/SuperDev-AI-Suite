"""Accuracy evaluation."""
from __future__ import annotations
from typing import Any, Dict, List

class AccuracyEvaluator:
    def __init__(self) -> None:
        self._evaluations: List[Dict[str, Any]] = []
    def evaluate(self, predictions: List[str], expected: List[str]) -> Dict[str, Any]:
        correct = sum(1 for p, e in zip(predictions, expected) if p.strip().lower() == e.strip().lower())
        total = len(expected)
        accuracy = (correct / total * 100) if total > 0 else 0
        result = {"accuracy": accuracy, "correct": correct, "total": total}
        self._evaluations.append(result)
        return result
    def evaluate_contains(self, predictions: List[str], expected_keywords: List[List[str]]) -> Dict[str, Any]:
        correct = 0
        for pred, keywords in zip(predictions, expected_keywords):
            if any(kw.lower() in pred.lower() for kw in keywords):
                correct += 1
        total = len(expected_keywords)
        accuracy = (correct / total * 100) if total > 0 else 0
        return {"accuracy": accuracy, "correct": correct, "total": total}
    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._evaluations[-limit:]
    def average_accuracy(self) -> float:
        if not self._evaluations:
            return 0.0
        return sum(e["accuracy"] for e in self._evaluations) / len(self._evaluations)
    def count(self) -> int:
        return len(self._evaluations)
    def clear(self) -> int:
        n = len(self._evaluations)
        self._evaluations.clear()
        return n
