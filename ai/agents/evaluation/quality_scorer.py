"""Quality scoring for agent outputs."""
from __future__ import annotations

from typing import Any


class QualityScorer:
    """Scores the quality of agent outputs against criteria."""

    def __init__(self) -> None:
        self._default_criteria = ["completeness", "clarity", "correctness", "efficiency"]

    def score(self, metrics: dict[str, Any]) -> dict[str, Any]:
        criteria_scores: dict[str, float] = {}
        for c in self._default_criteria:
            criteria_scores[c] = min(max(float(metrics.get(c, 0.5)), 0.0), 1.0)
        avg = sum(criteria_scores.values()) / max(len(criteria_scores), 1)
        return {"score": round(avg, 2), "criteria": criteria_scores}

    def score_output(self, output: dict[str, Any],
                     criteria: list[str] | None = None) -> dict[str, Any]:
        check_criteria = criteria or self._default_criteria
        scores: dict[str, float] = {}
        for c in check_criteria:
            if c in output:
                scores[c] = min(max(float(output[c]), 0.0), 1.0)
            elif c == "completeness":
                scores[c] = 1.0 if output else 0.0
            elif c == "clarity":
                text = str(output.get("content", ""))
                scores[c] = min(len(text) / 500, 1.0) if text else 0.3
            elif c == "correctness":
                scores[c] = float(output.get("confidence", 0.5))
            else:
                scores[c] = 0.5
        avg = sum(scores.values()) / max(len(scores), 1)
        return {
            "score": round(avg, 2),
            "criteria": scores,
            "grade": self._grade(avg),
        }

    def _grade(self, score: float) -> str:
        if score >= 0.9:
            return "A"
        if score >= 0.8:
            return "B"
        if score >= 0.6:
            return "C"
        if score >= 0.4:
            return "D"
        return "F"
