"""Core engine for test generation and execution."""

from typing import Any

from .models import TestCase, TestConfiguration, TestResult, TestSuite
from .test_generator import TestGenerator
from .test_reporter import TestReporter
from .test_runner import TestRunner


class TestingEngine:
    """Central engine coordinating test operations."""

    def __init__(self):
        self.generator = TestGenerator()
        self.runner = TestRunner()
        self.reporter = TestReporter()
        self._suites: dict[str, TestSuite] = {}
        self._results: list[TestResult] = []
        self._config = TestConfiguration()

    def create_suite(self, name: str, description: str = "") -> TestSuite:
        suite = TestSuite(name=name, description=description)
        self._suites[suite.suite_id] = suite
        return suite

    def add_test_to_suite(self, suite_id: str, test: TestCase) -> bool:
        suite = self._suites.get(suite_id)
        if not suite:
            return False
        suite.add_test(test)
        return True

    def generate_tests(self, module_path: str, category: str = "unit") -> TestSuite:
        from .models import TestCategory

        try:
            cat = TestCategory(category)
        except ValueError:
            cat = TestCategory.UNIT
        tests = self.generator.generate_for_module(module_path, cat)
        suite = TestSuite(name=f"Generated_{module_path}", tests=tests)
        self._suites[suite.suite_id] = suite
        return suite

    def run_suite(self, suite_id: str) -> list[TestResult]:
        suite = self._suites.get(suite_id)
        if not suite:
            return []
        results = self.runner.run_suite(suite)
        self._results.extend(results)
        return results

    def get_results(self) -> list[TestResult]:
        return list(self._results)

    def get_report(self) -> dict[str, Any]:
        return self.reporter.generate_report(self._results)

    def get_stats(self) -> dict[str, Any]:
        total = len(self._results)
        passed = sum(1 for r in self._results if r.is_passed())
        return {
            "suites": len(self._suites),
            "total_results": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total if total > 0 else 0.0,
        }
