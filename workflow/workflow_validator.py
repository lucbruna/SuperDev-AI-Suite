from __future__ import annotations

from typing import Any

from .workflow_models import WorkflowDefinition


class WorkflowValidator:
    """Validates workflow definitions and state."""

    def validate(self, definition: WorkflowDefinition) -> list[str]:
        errors: list[str] = []
        if not definition.name:
            errors.append("Workflow name is required")
        if not definition.steps:
            errors.append("Workflow must have at least one step")
        step_ids = set()
        for step in definition.steps:
            if not step.id:
                errors.append("Each step must have an id")
            if step.id in step_ids:
                errors.append(f"Duplicate step id: {step.id}")
            step_ids.add(step.id)
            if not step.action:
                errors.append(f"Step {step.id} has no action")
            for dep in step.depends_on:
                if dep not in step_ids and dep != step.id:
                    errors.append(
                        f"Step {step.id} depends on unknown step: {dep}"
                    )
        return errors

    def is_valid(self, definition: WorkflowDefinition) -> bool:
        return len(self.validate(definition)) == 0
