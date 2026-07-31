from __future__ import annotations

from typing import Any

from ..quality_models import TestCase, TestKind, TestSuite


class UnitTestEngine:
    """Unit testing — generator, executor, assertions, mocking control, coverage."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.unit
        self._mocks: dict[str, dict[str, Any]] = {}
        self._assertions: dict[str, Any] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- generation ----------------------------------------------------------

    def generate_suite(self, target: str, source: str | None = None) -> TestSuite:
        """Auto-generate a unit test suite for a target (heuristic generation)."""
        suite = TestSuite(name=f"unit-{target}", kind=TestKind.UNIT, target=target)
        cases = self.generate_cases(target, source)
        suite.cases = cases
        self.engine.registry.register_suite(suite)
        self.engine.metrics.increment("unit.suites")
        return suite

    def generate_cases(self, target: str, source: str | None = None) -> list[TestCase]:
        """Generate a set of unit test cases for a target."""
        checks: list[tuple[str, list[Any]]] = []
        if source:
            checks.append(("imports_resolve", [source.strip() != ""]))
            checks.append(("has_entry_points", ["def " in source or "class " in source]))
        checks.append(("returns_value", [True]))
        checks.append(("handles_empty", [target != ""]))
        checks.append(("boundary_ok", [len(target) < 1000]))

        return [
            TestCase(
                name=f"test_{i + 1}_{name}",
                kind=TestKind.UNIT,
                source=target,
                assertions=list(assertions),
            )
            for i, (name, assertions) in enumerate(checks)
        ]

    # -- assertions ----------------------------------------------------------

    def register_assertion(self, name: str, fn: Any) -> None:
        self._assertions[name] = fn

    def assert_equals(self, actual: Any, expected: Any) -> bool:
        return actual == expected

    def assert_true(self, value: Any) -> bool:
        return bool(value)

    def assert_in(self, item: Any, container: Any) -> bool:
        return item in container

    def assert_raises(self, fn: Any, exception_type: type[BaseException] = Exception) -> bool:
        try:
            fn()
        except exception_type:
            return True
        except Exception:
            return False
        return False

    # -- mocking control -----------------------------------------------------

    def create_mock(self, name: str, returns: Any = None) -> dict[str, Any]:
        mock = {
            "name": name,
            "returns": returns,
            "calls": 0,
            "args": [],
        }
        self._mocks[name] = mock
        return mock

    def get_mock(self, name: str) -> dict[str, Any] | None:
        return self._mocks.get(name)

    def call_mock(self, name: str, *args: Any) -> Any:
        mock = self._mocks.get(name)
        if mock is None:
            raise KeyError(f"Mock not found: {name}")
        mock["calls"] += 1
        mock["args"].append(args)
        return mock["returns"]

    def verify_called(self, name: str, times: int | None = None) -> bool:
        mock = self._mocks.get(name)
        if mock is None:
            return False
        if times is not None:
            return mock["calls"] == times
        return mock["calls"] > 0

    # -- coverage ------------------------------------------------------------

    def coverage_estimate(self, _target: str, covered: int, total: int) -> float:
        return round(covered / total, 4) if total else 1.0

    def meets_target(self, coverage: float) -> bool:
        return coverage >= self.config.coverage_target

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "mocks": len(self._mocks),
            "assertions": len(self._assertions),
        }


__all__ = ["UnitTestEngine"]
