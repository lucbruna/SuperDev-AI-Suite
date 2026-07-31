"""Evaluation engine for reasoning quality assessment."""

from __future__ import annotations

from typing import Any


class ReasoningEvaluator:
    """Evaluates the quality and soundness of reasoning outputs."""

    def __init__(self) -> None:
        self._evaluation_count: int = 0

    def evaluate(self, hypothesis: str, facts: dict[str, Any]) -> float:
        self._evaluation_count += 1
        score = 0.3
        if facts:
            score += min(len(facts) * 0.05, 0.3)
        hyp_words = set(hypothesis.lower().split())
        fact_values = set(str(v).lower() for v in facts.values())
        overlap = len(hyp_words & fact_values)
        score += min(overlap * 0.1, 0.2)
        if len(hypothesis) > 20:
            score += 0.1
        return min(round(score, 2), 1.0)

    def evaluate_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        confidence = decision.get("confidence", 0.5)
        alternatives_count = decision.get("alternatives_count", 0)
        quality = {
            "confidence_level": "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low",
            "choice_diversity": "good" if alternatives_count > 2 else "limited",
            "overall_quality": "strong" if confidence > 0.6 else "needs_review",
        }
        return quality

    def snapshot(self) -> dict[str, Any]:
        return {"total_evaluations": self._evaluation_count}
