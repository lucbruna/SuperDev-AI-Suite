from __future__ import annotations

from typing import Any


class PlanValidator:
    """Validates plans for correctness and feasibility."""

    def __init__(self) -> None:
        self._constraints: list[dict[str, Any]] = []

    def add_constraint(self, constraint: dict[str, Any]) -> None:
        self._constraints.append(constraint)

    async def validate(self, plan: dict[str, Any]) -> dict[str, Any]:
        errors: list[str] = []
        steps = plan.get("steps", [])
        if not steps:
            errors.append("Plan has no steps")
        for constraint in self._constraints:
            field = constraint.get("field", "")
            expected = constraint.get("value")
            actual = plan.get(field)
            if actual != expected:
                errors.append(f"{field}: expected {expected}, got {actual}")
        return {"valid": len(errors) == 0, "errors": errors, "step_count": len(steps)}

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        plan = context.get("plan", {})
        return await self.validate(plan)
