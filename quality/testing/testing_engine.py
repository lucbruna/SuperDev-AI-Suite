from __future__ import annotations

import time
from typing import Any

from ..quality_models import TestCase, TestKind, TestResult, TestStatus, TestSuite


class TestingEngine:
    """Main test motor — manager, runner, scheduler, executor, history."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.testing
        self._suites: dict[str, TestSuite] = {}
        self._results: dict[str, TestResult] = {}
        self._history: dict[str, list[TestResult]] = {}
        self._scheduled: list[dict[str, Any]] = []
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- suite management ----------------------------------------------------

    def register_suite(self, suite: TestSuite) -> TestSuite:
        self._suites[suite.suite_id] = suite
        self.engine.registry.register_suite(suite)
        return suite

    def create_suite(
        self,
        name: str,
        target: str = "",
        kind: TestKind = TestKind.UNIT,
    ) -> TestSuite:
        suite = TestSuite(name=name, target=target, kind=kind)
        return self.register_suite(suite)

    def add_case(self, suite_id: str, case: TestCase) -> bool:
        suite = self._suites.get(suite_id)
        if not suite:
            return False
        suite.cases.append(case)
        return True

    def get_suite(self, suite_id: str) -> TestSuite | None:
        return self._suites.get(suite_id)

    def list_suites(self) -> list[TestSuite]:
        return list(self._suites.values())

    # -- runner --------------------------------------------------------------

    async def run_case(self, case: TestCase) -> TestResult:
        """Run a single case and produce a result."""
        started = time.perf_counter()
        case.status = TestStatus.RUNNING
        try:
            passed = self.evaluate(case)
        except Exception as exc:  # noqa: BLE001 - test execution captures all errors
            case.status = TestStatus.ERROR
            case.error = str(exc)
            passed = False
        duration_ms = (time.perf_counter() - started) * 1000
        case.duration_ms = round(duration_ms, 2)
        case.status = TestStatus.PASSED if passed else TestStatus.FAILED

        result = TestResult(
            suite_id="",
            suite_name=case.name,
            kind=case.kind,
            total=1,
            passed=1 if passed else 0,
            failed=0 if passed else 1,
            duration_ms=round(duration_ms, 2),
            status=TestStatus.PASSED if passed else TestStatus.FAILED,
        )
        self._results[result.result_id] = result
        self.engine.registry.register_result(result)
        self.engine.metrics.increment(
            "testing.cases", labels={"status": case.status.value}
        )
        return result

    async def run_suite(
        self,
        suite: TestSuite,
        _config: dict[str, Any] | None = None,
    ) -> TestResult:
        """Run every case in a suite and aggregate the outcome."""
        started = time.perf_counter()
        passed = 0
        failed = 0
        skipped = 0
        errors = 0
        for case in suite.cases:
            if case.status == TestStatus.SKIPPED:
                skipped += 1
                continue
            try:
                case_passed = self.evaluate(case)
            except Exception as exc:  # noqa: BLE001
                case_passed = False
                case.error = str(exc)
                errors += 1
            case.status = TestStatus.PASSED if case_passed else TestStatus.FAILED
            if case_passed:
                passed += 1
            else:
                failed += 1

        duration_ms = (time.perf_counter() - started) * 1000
        result = TestResult(
            suite_id=suite.suite_id,
            suite_name=suite.name,
            kind=suite.kind,
            total=len(suite.cases),
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            duration_ms=round(duration_ms, 2),
            status=TestStatus.PASSED if failed == 0 and errors == 0 else TestStatus.FAILED,
        )
        self._results[result.result_id] = result
        self._history.setdefault(suite.suite_id, []).append(result)
        self.engine.registry.register_result(result)
        self.engine.metrics.increment(
            "testing.suites", labels={"status": result.status.value}
        )
        return result

    def evaluate(self, test_case: TestCase) -> bool:
        """Evaluate a case by running its assertions (default: all must be truthy)."""
        if not test_case.assertions:
            return True
        return all(bool(a) for a in test_case.assertions)

    # -- scheduler -----------------------------------------------------------

    def schedule(self, suite_id: str, at: float | None = None) -> bool:
        if suite_id not in self._suites:
            return False
        self._scheduled.append({
            "suite_id": suite_id,
            "at": at if at is not None else time.time(),
            "executed": False,
        })
        return True

    def due_suites(self, now: float | None = None) -> list[str]:
        now = now if now is not None else time.time()
        return [s["suite_id"] for s in self._scheduled if not s["executed"] and s["at"] <= now]

    # -- history -------------------------------------------------------------

    def history(self, suite_id: str) -> list[TestResult]:
        return list(self._history.get(suite_id, []))

    def latest_results(self, limit: int = 100) -> list[TestResult]:
        return sorted(
            self._results.values(),
            key=lambda r: r.started_at,
            reverse=True,
        )[:limit]

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "suites": len(self._suites),
            "results": len(self._results),
            "scheduled": len(self._scheduled),
        }


__all__ = ["TestingEngine"]
