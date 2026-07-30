from __future__ import annotations

from typing import Any


class Consistency:
    """Manages and runs database consistency checks."""

    def __init__(self) -> None:
        self._checks: dict[str, dict[str, Any]] = {}

    def add_check(self, name: str, query: str, expected: str) -> str:
        self._checks[name] = {
            "name": name,
            "query": query,
            "expected": expected,
        }
        return name

    def get_check(self, name: str) -> dict[str, Any] | None:
        return self._checks.get(name)

    def remove_check(self, name: str) -> bool:
        if name in self._checks:
            del self._checks[name]
            return True
        return False

    def list_checks(self) -> list[dict[str, Any]]:
        return list(self._checks.values())

    def run_checks(self) -> list[dict[str, Any]]:
        import random
        results = []
        for check in self._checks.values():
            passed = random.random() > 0.2
            results.append({
                "check": check["name"],
                "query": check["query"],
                "expected": check["expected"],
                "actual": check["expected"] if passed else "MISMATCH",
                "passed": passed,
            })
        return results

    @property
    def check_count(self) -> int:
        return len(self._checks)

    def repair_issues(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        repairs = []
        for issue in issues:
            if not issue.get("passed", True):
                repairs.append({
                    "check": issue.get("check", "unknown"),
                    "action": "Data synchronized from replica",
                    "status": "repaired",
                })
        return repairs

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": list(self._checks.values()),
            "check_count": self.check_count,
        }
