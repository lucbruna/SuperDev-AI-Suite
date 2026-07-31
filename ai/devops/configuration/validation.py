"""Config validation."""
from __future__ import annotations
from typing import Any, Dict, List

class ConfigValidator:
    def __init__(self) -> None:
        self._rules: List[Dict[str, Any]] = []
    def add_rule(self, name: str, field: str, rule_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        rule = {"name": name, "field": field, "type": rule_type, "params": params or {}}
        self._rules.append(rule)
        return rule
    def validate(self, config: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        for rule in self._rules:
            field = rule["field"]
            if rule["type"] == "required" and field not in config:
                errors.append({"field": field, "error": "required"})
            elif rule["type"] == "type" and field in config:
                expected = rule["params"].get("type", "")
                actual = type(config[field]).__name__
                if actual != expected:
                    errors.append({"field": field, "error": f"expected {expected}, got {actual}"})
        return {"valid": len(errors) == 0, "errors": errors}
    def list_rules(self) -> List[Dict[str, Any]]:
        return self._rules
    def clear_rules(self) -> int:
        n = len(self._rules)
        self._rules.clear()
        return n
    def count(self) -> int:
        return len(self._rules)
