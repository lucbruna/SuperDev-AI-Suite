from __future__ import annotations

import re
from typing import Any

BUILTIN_RULES: dict[str, tuple[str, str]] = {
    "email": (r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", "Must be a valid email"),
    "required": (r".+", "This field is required"),
    "min_length_3": (r".{3,}", "Must be at least 3 characters"),
    "min_length_8": (r".{8,}", "Must be at least 8 characters"),
    "url": (r"^https?://.*", "Must be a valid URL"),
    "numeric": (r"^\d+$", "Must contain only digits"),
    "alpha": (r"^[a-zA-Z]+$", "Must contain only letters"),
}


class Validation:
    """Manages validation rules and validates values."""

    def __init__(self) -> None:
        self._rules: dict[str, dict[str, Any]] = {}
        for name, (pattern, message) in BUILTIN_RULES.items():
            self._rules[name] = {"name": name, "pattern": pattern, "message": message}

    def add_rule(self, name: str, pattern: str, message: str) -> str:
        self._rules[name] = {"name": name, "pattern": pattern, "message": message}
        return name

    def get_rule(self, name: str) -> dict[str, Any] | None:
        return self._rules.get(name)

    def remove_rule(self, name: str) -> bool:
        if name in self._rules:
            del self._rules[name]
            return True
        return False

    def list_rules(self) -> list[dict[str, Any]]:
        return list(self._rules.values())

    def validate(self, value: str, rules: list[str]) -> list[dict[str, Any]]:
        results = []
        for rule_name in rules:
            rule = self._rules.get(rule_name)
            if rule is None:
                results.append({"rule": rule_name, "valid": False, "message": f"Unknown rule '{rule_name}'"})
                continue
            try:
                valid = bool(re.match(rule["pattern"], value))
            except re.error:
                valid = False
            results.append(
                {
                    "rule": rule_name,
                    "valid": valid,
                    "message": rule["message"] if not valid else "",
                }
            )
        return results

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    def to_dict(self) -> dict[str, Any]:
        return {
            "rules": list(self._rules.values()),
            "rule_count": self.rule_count,
        }
