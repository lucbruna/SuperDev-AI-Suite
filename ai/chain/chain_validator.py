from __future__ import annotations

from typing import Any


class ChainValidator:
    """Validates reasoning chain structure and completeness."""

    def __init__(self) -> None:
        self._constraints: list[dict[str, Any]] = []

    def add_constraint(self, constraint: dict[str, Any]) -> None:
        self._constraints.append(constraint)

    async def validate(self, chain: dict[str, Any]) -> dict[str, Any]:
        errors: list[str] = []
        steps = chain.get("steps", [])
        if not steps:
            errors.append("Chain has no steps")
        step_ids = [s.get("id") for s in steps]
        if len(step_ids) != len(set(step_ids)):
            errors.append("Duplicate step IDs found")
        for constraint in self._constraints:
            field = constraint.get("field", "")
            expected = constraint.get("value")
            actual = chain.get(field)
            if actual != expected:
                errors.append(f"{field}: expected {expected}, got {actual}")
        return {"valid": len(errors) == 0, "errors": errors, "step_count": len(steps)}
