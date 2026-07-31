"""Manager for test configurations and lifecycle."""

from typing import Any

from .models import TestConfiguration, TestResult, TestSuite


class TestingManager:
    """Manages test configurations and coordinates test operations."""

    def __init__(self):
        self._configurations: dict[str, TestConfiguration] = {}
        self._suites: dict[str, TestSuite] = {}
        self._results: list[TestResult] = []

    def create_configuration(self, name: str, **kwargs) -> TestConfiguration:
        config = TestConfiguration(name=name, **kwargs)
        self._configurations[config.config_id] = config
        return config

    def get_configuration(self, config_id: str) -> TestConfiguration | None:
        return self._configurations.get(config_id)

    def register_suite(self, suite: TestSuite) -> None:
        self._suites[suite.suite_id] = suite

    def get_suite(self, suite_id: str) -> TestSuite | None:
        return self._suites.get(suite_id)

    def add_result(self, result: TestResult) -> None:
        self._results.append(result)

    def get_results_for_suite(self, suite_id: str) -> list[TestResult]:
        suite = self._suites.get(suite_id)
        if not suite:
            return []
        test_ids = {t.test_id for t in suite.tests}
        return [r for r in self._results if r.test_id in test_ids]

    def get_statistics(self) -> dict[str, Any]:
        total = len(self._results)
        passed = sum(1 for r in self._results if r.is_passed())
        return {
            "configurations": len(self._configurations),
            "suites": len(self._suites),
            "total_results": total,
            "passed": passed,
            "failed": total - passed,
        }
