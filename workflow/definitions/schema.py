from __future__ import annotations

from typing import Any


class WorkflowSchema:
    """JSON schema validation for workflow definitions."""

    REQUIRED_STEP_FIELDS = {"id", "name", "action"}
    OPTIONAL_STEP_FIELDS = {"depends_on", "max_retries", "timeout", "params"}

    @classmethod
    def validate(cls, definition: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        if not isinstance(definition, dict):
            errors.append("Definition must be a dict")
            return errors
        if "name" not in definition:
            errors.append("Missing required field: name")
        if "steps" not in definition or not isinstance(definition["steps"], list):
            errors.append("Missing or invalid field: steps (must be a list)")
        else:
            for i, step in enumerate(definition["steps"]):
                for field in cls.REQUIRED_STEP_FIELDS:
                    if field not in step:
                        errors.append(f"Step {i} missing required field: {field}")
        return errors

    @classmethod
    def is_valid(cls, definition: dict[str, Any]) -> bool:
        return len(cls.validate(definition)) == 0
