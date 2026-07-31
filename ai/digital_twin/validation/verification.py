"""Verification."""
from __future__ import annotations
from typing import Any, Dict, List

class VerificationEngine:
    def __init__(self) -> None:
        self._checks: List[Dict[str, Any]] = []
        self._results: List[Dict[str, Any]] = []
    def add_check(self, name: str, description: str = "") -> Dict[str, Any]:
        check = {"name": name, "description": description}
        self._checks.append(check)
        return check
    def verify(self, check_name: str, data: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        mismatches = []
        for key in expected:
            if key not in data:
                mismatches.append({"field": key, "error": "missing"})
            elif data[key] != expected[key]:
                mismatches.append({"field": key, "actual": data[key], "expected": expected[key]})
        passed = len(mismatches) == 0
        result = {"check": check_name, "passed": passed, "mismatches": mismatches}
        self._results.append(result)
        return result
    def verify_schema(self, data: Dict[str, Any], schema: Dict[str, str]) -> Dict[str, Any]:
        errors = []
        for field, expected_type in schema.items():
            if field not in data:
                errors.append({"field": field, "error": "missing"})
            else:
                actual_type = type(data[field]).__name__
                if actual_type != expected_type:
                    errors.append({"field": field, "error": f"expected {expected_type}, got {actual_type}"})
        return {"valid": len(errors) == 0, "errors": errors}
    def get_results(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._results[-limit:]
    def pass_rate(self) -> float:
        if not self._results:
            return 0.0
        passed = sum(1 for r in self._results if r["passed"])
        return passed / len(self._results) * 100
    def count(self) -> int:
        return len(self._results)
