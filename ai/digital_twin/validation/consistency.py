"""Consistency validation."""

from __future__ import annotations

from typing import Any


class ConsistencyValidator:
    def __init__(self) -> None:
        self._rules: list[dict[str, Any]] = []
        self._violations: list[dict[str, Any]] = []

    def add_rule(self, name: str, rule_type: str, parameters: dict[str, Any]) -> dict[str, Any]:
        rule = {"name": name, "type": rule_type, "parameters": parameters}
        self._rules.append(rule)
        return rule

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        violations = []
        for rule in self._rules:
            if rule["type"] == "field_exists":
                field = rule["parameters"].get("field", "")
                if field not in data:
                    violations.append({"rule": rule["name"], "error": f"field {field} missing"})
            elif rule["type"] == "type_check":
                field = rule["parameters"].get("field", "")
                expected_type = rule["parameters"].get("type", "")
                if field in data:
                    actual_type = type(data[field]).__name__
                    if actual_type != expected_type:
                        violations.append(
                            {"rule": rule["name"], "error": f"expected {expected_type}, got {actual_type}"}
                        )
            elif rule["type"] == "range":
                field = rule["parameters"].get("field", "")
                min_val = rule["parameters"].get("min", 0)
                max_val = rule["parameters"].get("max", 100)
                if field in data and isinstance(data[field], (int, float)):
                    if data[field] < min_val or data[field] > max_val:
                        violations.append({"rule": rule["name"], "error": "out of range"})
        valid = len(violations) == 0
        if not valid:
            self._violations.extend(violations)
        return {"valid": valid, "violations": violations}

    def get_violations(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._violations[-limit:]

    def list_rules(self) -> list[dict[str, Any]]:
        return self._rules

    def violation_count(self) -> int:
        return len(self._violations)

    def clear_violations(self) -> int:
        n = len(self._violations)
        self._violations.clear()
        return n
