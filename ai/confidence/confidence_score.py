from __future__ import annotations

from typing import Any


class ConfidenceScore:
    """Computes confidence scores from evidence."""

    def __init__(self) -> None:
        self._base_score: float = 0.5

    def set_base(self, score: float) -> None:
        self._base_score = max(0.0, min(1.0, score))

    async def compute(self, context: dict[str, Any]) -> float:
        evidence_strength = context.get("evidence_strength", 0.5)
        model_certainty = context.get("model_certainty", 0.5)
        historical_accuracy = context.get("historical_accuracy", 0.5)
        score = (evidence_strength + model_certainty + historical_accuracy) / 3
        return max(0.0, min(1.0, score))
