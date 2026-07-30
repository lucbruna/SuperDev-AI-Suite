from __future__ import annotations

from typing import Any

from .reasoning_models import ReasoningResult


class ReasoningValidator:
    """Validates reasoning outputs and intermediate results."""

    @staticmethod
    def validate_result(result: ReasoningResult) -> dict[str, Any]:
        errors: list[str] = []
        if not result.decision:
            errors.append("Empty decision")
        if result.confidence < 0 or result.confidence > 1:
            errors.append("Confidence out of range [0, 1]")
        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_confidence(confidence: float, threshold: float = 0.5) -> bool:
        return 0 <= confidence <= 1 and confidence >= threshold

    @staticmethod
    def validate_hypothesis(hypothesis: str) -> dict[str, Any]:
        errors: list[str] = []
        if not hypothesis or not hypothesis.strip():
            errors.append("Hypothesis is empty")
        return {"valid": len(errors) == 0, "errors": errors}
