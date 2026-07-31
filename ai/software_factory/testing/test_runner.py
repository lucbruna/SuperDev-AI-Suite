"""Runner for executing test suites."""

from datetime import datetime
from typing import Any

from .models import TestCase, TestResult, TestStatus, TestSuite


class TestRunner:
    """Executes test suites and collects results."""

    def __init__(self):
        self._running = False
        self._execution_history: list[dict[str, Any]] = []

    def run_suite(self, suite: TestSuite) -> list[TestResult]:
        """Run all enabled tests in a suite."""
        results = []
        self._running = True
        for test in suite.tests:
            if test.enabled:
                result = self._run_single(test)
                results.append(result)
        self._running = False
        self._execution_history.append(
            {
                "suite": suite.name,
                "tests_run": len(results),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        return results

    def _run_single(self, test: TestCase) -> TestResult:
        """Execute a single test case."""
        datetime.utcnow()
        try:
            # Simulate test execution
            result = TestResult(
                test_id=test.test_id,
                test_name=test.name,
                status=TestStatus.PASSED,
                duration=0.001,
                assertions_passed=1,
                assertions_failed=0,
            )
        except Exception as e:
            result = TestResult(
                test_id=test.test_id,
                test_name=test.name,
                status=TestStatus.FAILED,
                message=str(e),
            )
        return result

    def run_test(self, test: TestCase) -> TestResult:
        return self._run_single(test)

    def is_running(self) -> bool:
        return self._running

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._execution_history)
