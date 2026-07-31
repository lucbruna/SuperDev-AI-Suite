"""Testing & Quality Engine — SuperDev AI Suite Volume 15.

Validates, tests and monitors everything the SuperDev AI Suite generates:
unit/integration/regression/performance/security tests, code coverage,
intelligent analysis, benchmarking, quality reports and the production gate
that approves or blocks deliveries.
"""
from __future__ import annotations

from .analysis.analyzer_engine import AnalyzerEngine
from .automation.automation_engine import AutomationEngine
from .benchmarking.benchmark_engine import BenchmarkEngine
from .coverage.coverage_engine import CoverageEngine
from .integration.integration_engine import IntegrationEngine
from .performance.performance_engine import PerformanceEngine
from .quality_config import QualityConfig
from .quality_context import QualityContext
from .quality_engine import QualityEngine
from .quality_events import QualityEventBus
from .quality_factory import QualityFactory
from .quality_logger import QualityLogger
from .quality_manager import QualityManager
from .quality_metrics import QualityMetrics
from .quality_models import (
    CoverageReport,
    CoverageType,
    GateDecision,
    PerformanceReport,
    ProductionGate,
    QualityScore,
    TestCase,
    TestKind,
    TestResult,
    TestSeverity,
    TestStatus,
    TestSuite,
    VulnerabilityFinding,
)
from .quality_protocols import result_to_dict
from .quality_registry import QualityRegistry
from .quality_runtime import QualityRuntime
from .quality_security import QualitySecurity
from .regression.regression_engine import RegressionEngine
from .reports.report_engine import QualityReportEngine
from .security.security_test_engine import SecurityTestEngine
from .testing.testing_engine import TestingEngine
from .unit.unit_test_engine import UnitTestEngine
from .validation.validation_engine import ValidationEngine

__version__ = "1.0.0"
__all__ = [
    "QualityConfig", "QualityContext", "QualityEngine", "QualityEventBus",
    "QualityFactory", "QualityLogger", "QualityManager", "QualityMetrics",
    "QualityRegistry", "QualityRuntime", "QualitySecurity",
    # Models
    "CoverageReport", "CoverageType", "GateDecision", "PerformanceReport",
    "ProductionGate", "QualityScore", "TestCase", "TestKind", "TestResult",
    "TestSeverity", "TestStatus", "TestSuite", "VulnerabilityFinding",
    "result_to_dict",
    # Subsystem engines
    "TestingEngine", "UnitTestEngine", "IntegrationEngine", "RegressionEngine",
    "PerformanceEngine", "SecurityTestEngine", "AutomationEngine",
    "CoverageEngine", "AnalyzerEngine", "BenchmarkEngine",
    "QualityReportEngine", "ValidationEngine",
]
