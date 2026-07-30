from __future__ import annotations

from typing import Any

from .workflow_definition import WorkflowDefinition


class DefinitionValidator:
    """Validates parsed workflow definitions."""

    @staticmethod
    def validate(definition: WorkflowDefinition) -> list[str]:
        errors: list[str] = []
        if not definition.name:
            errors.append("Workflow name cannot be empty")
        if not definition.steps:
            errors.append("Workflow must have at least one step")
        step_ids = set()
        for i, step in enumerate(definition.steps):
            sid = step.get("id", f"step_{i}")
            if sid in step_ids:
                errors.append(f"Duplicate step id: {sid}")
            step_ids.add(sid)
            if not step.get("action"):
                errors.append(f"Step {sid} has no action")
        for step in definition.steps:
            for dep in step.get("depends_on", []):
                if dep not in step_ids:
                    errors.append(f"Step {step['id']} depends on unknown: {dep}")
        return errors

    @staticmethod
    def is_valid(definition: WorkflowDefinition) -> bool:
        return len(DefinitionValidator.validate(definition)) == 0
