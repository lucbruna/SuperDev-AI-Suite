from __future__ import annotations

from typing import Any


class ValidationResult:
    """Result of a context validation."""

    def __init__(self, valid: bool, errors: list[str] | None = None):
        self._valid = valid
        self._errors = list(errors) if errors else []

    @property
    def valid(self) -> bool:
        return self._valid

    @property
    def errors(self) -> list[str]:
        return list(self._errors)

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self._valid, "errors": list(self._errors)}


class ContextValidator:
    """Validates context structure, completeness, and constraints."""

    def __init__(self):
        self._validation_count: int = 0

    @property
    def validation_count(self) -> int:
        return self._validation_count

    def validate(self, context: dict[str, Any]) -> ValidationResult:
        errors: list[str] = []
        if not isinstance(context, dict):
            errors.append("Context must be a dict")
            return ValidationResult(False, errors)
        if "content" not in context:
            errors.append("Missing 'content' key")
        if "sources" not in context:
            errors.append("Missing 'sources' key")
        else:
            if not isinstance(context["sources"], list):
                errors.append("'sources' must be a list")
        self._validation_count += 1
        return ValidationResult(len(errors) == 0, errors)

    def validate_size(self, context: dict[str, Any], max_size: int = 1_000_000) -> ValidationResult:
        errors: list[str] = []
        import json

        try:
            size = len(json.dumps(context))
            if size > max_size:
                errors.append(f"Context size {size} exceeds max {max_size}")
        except Exception:
            errors.append("Could not serialize context for size check")
        self._validation_count += 1
        return ValidationResult(len(errors) == 0, errors)

    def validate_schema(self, context: dict[str, Any], schema: dict[str, type]) -> ValidationResult:
        errors: list[str] = []
        for key, expected_type in schema.items():
            if key not in context:
                errors.append(f"Missing key: {key}")
            elif not isinstance(context[key], expected_type):
                errors.append(f"Key '{key}' expected {expected_type.__name__}, got {type(context[key]).__name__}")
        self._validation_count += 1
        return ValidationResult(len(errors) == 0, errors)

    def reset(self) -> None:
        self._validation_count = 0
