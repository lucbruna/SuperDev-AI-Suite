"""Manager for test configurations and lifecycle."""
from typing import List, Dict, Any, Optional
from .models import TestConfiguration, TestSuite, TestCase, TestResult


class TestingManager:
    """Manages test configurations and coordinates test operations."""

    def __init__(self):
        self._configurations: Dict[str, TestConfiguration] = {}
        self._suites: Dict[str, TestSuite] = {}
        self._results: List[TestResult] = []

    def create_configuration(self, name: str, **kwargs) -> TestConfiguration:
        config = TestConfiguration(name=name, **kwargs)
        self._configurations[config.config_id] = config
        return config

    def get_configuration(self, config_id: str) -> Optional[TestConfiguration]:
        return self._configurations.get(config_id)

    def register_suite(self, suite: TestSuite) -> None:
        self._suites[suite.suite_id] = suite

    def get_suite(self, suite_id: str) -> Optional[TestSuite]:
        return self._suites.get(suite_id)

    def add_result(self, result: TestResult) -> None:
        self._results.append(result)

    def get_results_for_suite(self, suite_id: str) -> List[TestResult]:
        suite = self._suites.get(suite_id)
        if not suite:
            return []
        test_ids = {t.test_id for t in suite.tests}
        return [r for r in self._results if r.test_id in test_ids]

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self._results)
        passed = sum(1 for r in self._results if r.is_passed())
        return {
            "configurations": len(self._configurations),
            "suites": len(self._suites),
            "total_results": total,
            "passed": passed,
            "failed": total - passed,
        }
