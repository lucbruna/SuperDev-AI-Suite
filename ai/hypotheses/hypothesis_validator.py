from __future__ import annotations

from typing import Any


class HypothesisValidator:
    """Validates hypotheses against known facts and constraints."""

    def __init__(self) -> None:
        self._constraints: list[dict[str, Any]] = []

    def add_constraint(self, constraint: dict[str, Any]) -> None:
        self._constraints.append(constraint)

    async def validate(self, hypothesis: dict[str, Any]) -> dict[str, Any]:
        issues: list[str] = []
        for constraint in self._constraints:
            field = constraint.get("field", "")
            if field in hypothesis:
                expected = constraint.get("value")
                if hypothesis[field] != expected:
                    issues.append(f"{field} does not match constraint")
        return {**hypothesis, "valid": len(issues) == 0, "issues": issues}

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        hypotheses = context.get("hypotheses", [])
        validated = [await self.validate(h) for h in hypotheses]
        return {"validated": validated, "valid_count": sum(1 for v in validated if v["valid"])}
