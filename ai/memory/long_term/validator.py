from __future__ import annotations

from typing import Any, Dict, List, Optional


class ValidationResult:
    """Result of a validation operation."""

    def __init__(self, valid: bool, errors: List[str] | None = None):
        self._valid = valid
        self._errors = errors or []

    @property
    def valid(self) -> bool:
        return self._valid

    @property
    def errors(self) -> List[str]:
        return list(self._errors)


class Validator:
    """Validator for long-term memory data integrity."""

    def validate(self, data: Any) -> bool:
        result = self.validate_detailed(data)
        return result.valid

    def validate_detailed(self, data: Any) -> ValidationResult:
        errors: List[str] = []
        if data is None:
            errors.append("Data cannot be None")
            return ValidationResult(False, errors)
        if not isinstance(data, dict):
            errors.append(f"Expected dict, got {type(data).__name__}")
            return ValidationResult(False, errors)
        if not data:
            errors.append("Data dict is empty")
        for key, value in data.items():
            if not isinstance(key, str):
                errors.append(f"Key must be string, got {type(key).__name__}: {key}")
            if value is None:
                errors.append(f"Value for key '{key}' is None")
        return ValidationResult(len(errors) == 0, errors)

    def validate_key(self, key: str) -> bool:
        if not key or not isinstance(key, str):
            return False
        if len(key) > 1024:
            return False
        return bool(key.strip())

    def validate_batch(self, items: Dict[str, Any]) -> Dict[str, List[str]]:
        results: Dict[str, List[str]] = {}
        for key, data in items.items():
            result = self.validate_detailed(data)
            if not result.valid:
                results[key] = result.errors
        return results
