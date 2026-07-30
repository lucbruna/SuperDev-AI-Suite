from __future__ import annotations

from typing import Any


class InferenceValidator:
    """Validates inference inputs and outputs."""

    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []

    def add_rule(self, rule: dict[str, Any]) -> None:
        self._rules.append(rule)

    async def validate(self, context: dict[str, Any]) -> dict[str, Any]:
        validated = dict(context)
        for rule in self._rules:
            field = rule.get("field", "")
            if field in validated:
                expected_type = rule.get("type")
                if expected_type and not isinstance(validated[field], expected_type):
                    validated[field] = None
        return validated

    async def verify(self, result: dict[str, Any], expected: dict[str, Any]) -> bool:
        for key, value in expected.items():
            if result.get(key) != value:
                return False
        return True
