"""Validation engine."""
from __future__ import annotations

from typing import Any


class ValidationEngine:
    def __init__(self) -> None:
        self._validators: dict[str, Any] = {}
        self._results: list[dict[str, Any]] = []
        self._started = False
    def start(self) -> None:
        self._started = True
    def register_validator(self, name: str, validator_type: str = "schema") -> dict[str, Any]:
        validator = {"name": name, "type": validator_type, "validations": 0, "passed": 0}
        self._validators[name] = validator
        return validator
    def validate(self, validator_name: str, data: dict[str, Any], rules: dict[str, Any] = None) -> dict[str, Any]:
        if validator_name not in self._validators:
            return {"error": "not_found"}
        self._validators[validator_name]["validations"] += 1
        errors = []
        if rules:
            for field, rule in rules.items():
                if rule.get("required") and field not in data:
                    errors.append({"field": field, "error": "required"})
                if "min" in rule and isinstance(data.get(field), (int, float)):
                    if data[field] < rule["min"]:
                        errors.append({"field": field, "error": "below_min"})
                if "max" in rule and isinstance(data.get(field), (int, float)):
                    if data[field] > rule["max"]:
                        errors.append({"field": field, "error": "above_max"})
        valid = len(errors) == 0
        if valid:
            self._validators[validator_name]["passed"] += 1
        result = {"validator": validator_name, "valid": valid, "errors": errors}
        self._results.append(result)
        return result
    def get_results(self, validator_name: str = "", limit: int = 20) -> list[dict[str, Any]]:
        results = self._results
        if validator_name:
            results = [r for r in results if r["validator"] == validator_name]
        return results[-limit:]
    def pass_rate(self, validator_name: str = "") -> float:
        if validator_name:
            v = self._validators.get(validator_name, {})
            total = v.get("validations", 0)
            passed = v.get("passed", 0)
            return (passed / total * 100) if total > 0 else 0
        total = sum(v.get("validations", 0) for v in self._validators.values())
        passed = sum(v.get("passed", 0) for v in self._validators.values())
        return (passed / total * 100) if total > 0 else 0
    def list_validators(self) -> list[dict[str, Any]]:
        return list(self._validators.values())
    def count(self) -> int:
        return len(self._results)
    def is_running(self) -> bool:
        return self._started
