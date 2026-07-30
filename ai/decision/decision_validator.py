from __future__ import annotations

from typing import Any

from .decision_models import DecisionResult


class DecisionValidator:
    """Validates decisions before and after execution."""

    @staticmethod
    def validate_options(options: list[str]) -> dict[str, Any]:
        errors: list[str] = []
        if not options:
            errors.append("No options provided")
        if len(options) < 2:
            errors.append("Need at least 2 options for a decision")
        has_empty = any(not o.strip() for o in options)
        if has_empty:
            errors.append("Some options are empty")
        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_result(result: DecisionResult) -> dict[str, Any]:
        errors: list[str] = []
        if not result.decision:
            errors.append("Empty decision")
        if result.confidence < 0 or result.confidence > 1:
            errors.append("Confidence out of range")
        return {"valid": len(errors) == 0, "errors": errors}
