from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class TestStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestKind(StrEnum):
    UNIT = "unit"
    INTEGRATION = "integration"
    REGRESSION = "regression"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UI = "ui"


class TestSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GateDecision(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    BLOCKED = "blocked"


class CoverageType(StrEnum):
    LINE = "line"
    BRANCH = "branch"
    FUNCTION = "function"


@dataclass
class TestCase:
    """A single test case with assertions and outcome."""

    case_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    name: str = ""
    kind: TestKind = TestKind.UNIT
    source: str = ""  # module / file under test
    assertions: list[str] = field(default_factory=list)
    status: TestStatus = TestStatus.PENDING
    duration_ms: float = 0.0
    error: str = ""
    created_at: float = field(default_factory=time.time)


@dataclass
class TestSuite:
    """A collection of test cases for a target."""

    suite_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    kind: TestKind = TestKind.UNIT
    target: str = ""  # component under test
    cases: list[TestCase] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class TestResult:
    """Outcome summary of a test run."""

    result_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    suite_id: str = ""
    suite_name: str = ""
    kind: TestKind = TestKind.UNIT
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration_ms: float = 0.0
    status: TestStatus = TestStatus.PENDING
    started_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        # Accept plain strings (e.g. "passed") and coerce to the enum so
        # callers can safely use `.value` when rendering.
        if isinstance(self.status, str):
            try:
                self.status = TestStatus(self.status)
            except ValueError:
                self.status = TestStatus.PENDING

    @property
    def passed_rate(self) -> float:
        return round(self.passed / self.total, 4) if self.total else 1.0


@dataclass
class CoverageReport:
    """Code coverage percentages for a target."""

    report_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    target: str = ""
    line: float = 0.0
    branch: float = 0.0
    function: float = 0.0
    covered_lines: int = 0
    total_lines: int = 0
    generated_at: float = field(default_factory=time.time)

    @property
    def overall(self) -> float:
        values = [v for v in (self.line, self.branch, self.function) if v > 0]
        return round(sum(values) / len(values), 4) if values else 0.0


@dataclass
class VulnerabilityFinding:
    """A security finding produced by the security subsystem."""

    finding_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    severity: TestSeverity = TestSeverity.MEDIUM
    title: str = ""
    description: str = ""
    location: str = ""
    recommendation: str = ""
    detected_at: float = field(default_factory=time.time)


@dataclass
class PerformanceReport:
    """Performance metrics for a target (latency, throughput, resources)."""

    report_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    target: str = ""
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    throughput: float = 0.0  # ops / second
    error_rate: float = 0.0
    peak_memory_mb: float = 0.0
    generated_at: float = field(default_factory=time.time)


@dataclass
class QualityScore:
    """Composite quality score across code, tests, security, performance, docs."""

    score_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    target: str = ""
    code: float = 0.0
    tests: float = 0.0
    security: float = 0.0
    performance: float = 0.0
    documentation: float = 0.0
    computed_at: float = field(default_factory=time.time)

    @property
    def overall(self) -> float:
        # Uniform weights across the five dimensions; dimensions that were
        # not provided (default 0.0) are excluded so the score reflects only
        # the dimensions actually measured.
        weights = {"code": 0.2, "tests": 0.2, "security": 0.2,
                   "performance": 0.2, "documentation": 0.2}
        provided = {key: getattr(self, key) for key in weights if getattr(self, key) > 0.0}
        if not provided:
            return 0.0
        total_weight = sum(weights[key] for key in provided)
        return round(
            sum(value * weights[key] for key, value in provided.items())
            / total_weight,
            4,
        )


@dataclass
class ProductionGate:
    """Result of the production gate validation."""

    gate_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    target: str = ""
    checks: list[dict[str, Any]] = field(default_factory=list)
    decision: GateDecision = GateDecision.PENDING
    quality_score: float = 0.0
    blocked_reasons: list[str] = field(default_factory=list)
    evaluated_at: float = field(default_factory=time.time)


__all__ = [
    "TestStatus", "TestKind", "TestSeverity", "GateDecision", "CoverageType",
    "TestCase", "TestSuite", "TestResult", "CoverageReport",
    "VulnerabilityFinding", "PerformanceReport", "QualityScore", "ProductionGate",
]
