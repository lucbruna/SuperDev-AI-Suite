"""Model validation."""
from __future__ import annotations
from typing import Any, Dict, List

class ModelValidator:
    def __init__(self) -> None:
        self._checks: List[Dict[str, Any]] = []
        self._results: List[Dict[str, Any]] = []
    def add_check(self, name: str, check_fn, description: str = "") -> Dict[str, Any]:
        check = {"name": name, "description": description}
        self._checks.append(check)
        return check
    def validate(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        passed = len(self._checks)
        failed = 0
        failures = []
        for check in self._checks:
            if check["name"] == "has_parameters":
                if not model_data.get("parameters"):
                    failed += 1
                    failures.append(check["name"])
            elif check["name"] == "has_config":
                if not model_data.get("config"):
                    failed += 1
                    failures.append(check["name"])
        result = {"passed": passed - failed, "failed": failed, "total": passed, "failures": failures, "valid": failed == 0}
        self._results.append(result)
        return result
    def validate_schema(self, data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        missing = [f for f in required_fields if f not in data]
        return {"valid": len(missing) == 0, "missing_fields": missing}
    def get_results(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._results[-limit:]
    def list_checks(self) -> List[str]:
        return [c["name"] for c in self._checks]
    def pass_rate(self) -> float:
        if not self._results:
            return 0.0
        passed = sum(1 for r in self._results if r["valid"])
        return passed / len(self._results)
    def count(self) -> int:
        return len(self._results)
