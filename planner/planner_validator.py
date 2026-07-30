from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .planner_models import Plan, Task, TaskStatus


class ValidationResult:
    """Result of a plan validation."""
    def __init__(self, is_valid: bool = True, errors: list[str] | None = None, warnings: list[str] | None = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
        self.timestamp = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": self.timestamp,
        }


class PlannerValidator:
    """Validates plans for correctness and completeness."""

    def validate(self, plan: Any) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        if not plan:
            return ValidationResult(is_valid=False, errors=["Plan is None"])

        if not getattr(plan, "goal", None):
            errors.append("Plan has no goal")

        tasks = getattr(plan, "tasks", [])
        if not tasks:
            warnings.append("Plan has no tasks")

        task_names = set()
        for i, task in enumerate(tasks):
            name = getattr(task, "name", f"task_{i}")
            if name in task_names:
                warnings.append(f"Duplicate task name: '{name}'")
            task_names.add(name)

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings)

    def estimate_duration(self, plan: Any) -> float:
        total = 0.0
        for task in getattr(plan, "tasks", []):
            total += getattr(task, "estimated_duration", 60.0)
        return total
