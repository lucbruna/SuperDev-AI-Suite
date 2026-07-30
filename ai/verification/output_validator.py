from __future__ import annotations

from typing import Any


class OutputValidator:
    """Validates output format and structure."""

    def __init__(self) -> None:
        self._format_rules: list[dict[str, Any]] = []

    def add_rule(self, rule: dict[str, Any]) -> None:
        self._format_rules.append(rule)

    async def validate(self, response: str, context: dict[str, Any]) -> dict[str, Any]:
        errors: list[str] = []
        for rule in self._format_rules:
            rule_type = rule.get("type", "")
            if rule_type == "max_length" and len(response) > rule.get("value", 0):
                errors.append(f"Response exceeds max length of {rule.get('value')}")
            if rule_type == "required_prefix" and not response.startswith(rule.get("value", "")):
                errors.append(f"Response must start with '{rule.get('value')}'")
            if rule_type == "required_suffix" and not response.endswith(rule.get("value", "")):
                errors.append(f"Response must end with '{rule.get('value')}'")
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "length": len(response),
        }
