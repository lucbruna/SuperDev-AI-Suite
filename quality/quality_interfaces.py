from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

from .quality_models import TestCase, TestResult, TestSuite


class ITestRunner(ABC):
    """Executes a suite of test cases."""

    @abstractmethod
    async def run(self, suite: TestSuite, config: dict[str, Any] | None = None) -> TestResult: ...

    @abstractmethod
    def evaluate(self, test_case: TestCase) -> bool: ...


class IQualityReporter(Protocol):
    """Renders quality artifacts to markdown/HTML/JSON."""

    def render(self, artifact: Any) -> str: ...


class IApprovalGate(ABC):
    """Approves or blocks a delivery based on quality signals."""

    @abstractmethod
    def evaluate(self, signals: dict[str, Any]) -> dict[str, Any]: ...


class ITestGenerator(Protocol):
    """Generates test cases for a target."""

    def generate(self, target: str, source: str | None = None) -> list[TestCase]: ...


__all__ = ["ITestRunner", "IQualityReporter", "IApprovalGate", "ITestGenerator"]
