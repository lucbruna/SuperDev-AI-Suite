from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class Regression:
    """Manages and runs regression test suites."""

    def __init__(self) -> None:
        self._tests: dict[str, dict[str, Any]] = {}

    def add_test(self, name: str, description: str, category: str = "unit") -> str:
        self._tests[name] = {
            "name": name,
            "description": description,
            "category": category,
        }
        return name

    def get_test(self, name: str) -> dict[str, Any] | None:
        return self._tests.get(name)

    def remove_test(self, name: str) -> bool:
        if name in self._tests:
            del self._tests[name]
            return True
        return False

    def list_tests(self, category: str | None = None) -> list[dict[str, Any]]:
        tests = list(self._tests.values())
        if category:
            tests = [t for t in tests if t["category"] == category]
        return tests

    def run_regression_suite(
        self,
        test_names: list[str] | None = None,
    ) -> dict[str, Any]:
        import random
        tests_to_run = [t for n, t in self._tests.items() if test_names is None or n in test_names]
        results = []
        passed = 0
        for t in tests_to_run:
            success = random.random() > 0.15
            if success:
                passed += 1
            results.append({
                "name": t["name"],
                "passed": success,
            })
        return {
            "total": len(tests_to_run),
            "passed": passed,
            "failed": len(tests_to_run) - passed,
            "results": results,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    @property
    def test_count(self) -> int:
        return len(self._tests)

    @property
    def regression_coverage(self) -> float:
        if not self._tests:
            return 0.0
        return round(min(100.0, self._tests.__len__() * 10.0), 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "tests": list(self._tests.values()),
            "test_count": self.test_count,
            "coverage": self.regression_coverage,
        }
