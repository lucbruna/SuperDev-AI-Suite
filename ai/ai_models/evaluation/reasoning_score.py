"""Reasoning score evaluation."""
from __future__ import annotations

from typing import Any


class ReasoningEvaluator:
    def __init__(self) -> None:
        self._results: list[dict[str, Any]] = []
    def evaluate(self, model_output: str, expected_reasoning: str, criteria: list[str] = None) -> dict[str, Any]:
        criteria = criteria or ["logic", "completeness", "clarity"]
        scores = {}
        for criterion in criteria:
            scores[criterion] = 0.8 if criterion in model_output.lower() else 0.5
        avg = sum(scores.values()) / len(scores) if scores else 0
        result = {"scores": scores, "avg_score": avg, "criteria": criteria}
        self._results.append(result)
        return result
    def evaluate_chain(self, steps: list[str], expected_steps: list[str]) -> dict[str, Any]:
        matched = sum(1 for s in steps if s in expected_steps)
        total = max(len(expected_steps), 1)
        score = (matched / total) * 100
        return {"score": score, "matched": matched, "total": len(expected_steps)}
    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._results[-limit:]
    def average_score(self) -> float:
        if not self._results:
            return 0.0
        return sum(r["avg_score"] for r in self._results) / len(self._results)
    def count(self) -> int:
        return len(self._results)
