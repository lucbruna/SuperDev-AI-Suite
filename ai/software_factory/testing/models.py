"""Data models for test management."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestCategory(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    PERFORMANCE = "performance"
    SECURITY = "security"
    SMOKE = "smoke"
    REGRESSION = "regression"


@dataclass
class TestCase:
    """A single test case."""

    test_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    category: TestCategory = TestCategory.UNIT
    module: str = ""
    method_name: str = ""
    assertions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    timeout: float = 30.0
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "test_id": self.test_id,
            "name": self.name,
            "category": self.category.value,
            "module": self.module,
        }


@dataclass
class TestSuite:
    """A collection of test cases."""

    suite_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    tests: list[TestCase] = field(default_factory=list)
    setup_code: str = ""
    teardown_code: str = ""

    def add_test(self, test: TestCase) -> None:
        self.tests.append(test)

    def get_by_category(self, category: TestCategory) -> list[TestCase]:
        return [t for t in self.tests if t.category == category]

    def enabled_count(self) -> int:
        return sum(1 for t in self.tests if t.enabled)


@dataclass
class TestResult:
    """Result of running a test."""

    result_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    test_id: str = ""
    test_name: str = ""
    status: TestStatus = TestStatus.PENDING
    duration: float = 0.0
    message: str = ""
    stack_trace: str = ""
    assertions_passed: int = 0
    assertions_failed: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def is_passed(self) -> bool:
        return self.status == TestStatus.PASSED


@dataclass
class CoverageReport:
    """Test coverage report."""

    report_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    total_lines: int = 0
    covered_lines: int = 0
    total_functions: int = 0
    covered_functions: int = 0
    files: dict[str, dict[str, int]] = field(default_factory=dict)

    @property
    def line_coverage(self) -> float:
        return self.covered_lines / self.total_lines if self.total_lines > 0 else 0.0

    @property
    def function_coverage(self) -> float:
        return self.covered_functions / self.total_functions if self.total_functions > 0 else 0.0


@dataclass
class TestConfiguration:
    """Test execution configuration."""

    config_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    test_dir: str = "tests"
    pattern: str = "test_*.py"
    parallel: bool = False
    max_workers: int = 4
    timeout: float = 60.0
    verbose: bool = True
    categories: list[TestCategory] = field(default_factory=lambda: list(TestCategory))
