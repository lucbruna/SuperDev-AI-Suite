from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class TestingConfig:
    enabled: bool = True
    default_timeout_s: float = 30.0
    parallel_enabled: bool = True
    max_parallel: int = 4
    retry_on_failure: bool = True
    max_retries: int = 2


@dataclass
class UnitConfig:
    enabled: bool = True
    auto_generate: bool = True
    assertion_style: str = "pytest"
    mocking_enabled: bool = True
    coverage_target: float = 0.8


@dataclass
class IntegrationConfig:
    enabled: bool = True
    api_tests_enabled: bool = True
    database_tests_enabled: bool = True
    workflow_tests_enabled: bool = True
    environment: str = "staging"


@dataclass
class RegressionConfig:
    enabled: bool = True
    baseline_enabled: bool = True
    auto_baseline: bool = True
    impact_analysis_enabled: bool = True


@dataclass
class PerformanceConfig:
    enabled: bool = True
    load_testing_enabled: bool = True
    stress_testing_enabled: bool = True
    latency_target_ms: float = 200.0
    throughput_target: float = 100.0


@dataclass
class SecurityConfig:
    enabled: bool = True
    vulnerability_scan_enabled: bool = True
    dependency_scan_enabled: bool = True
    penetration_enabled: bool = True
    fail_on_critical: bool = True


@dataclass
class AutomationConfig:
    enabled: bool = True
    test_generation_enabled: bool = True
    parallel_runner_enabled: bool = True
    notifications_enabled: bool = True
    schedule: str = ""


@dataclass
class CoverageConfig:
    enabled: bool = True
    line_target: float = 0.8
    branch_target: float = 0.7
    function_target: float = 0.9


@dataclass
class AnalysisConfig:
    enabled: bool = True
    complexity_enabled: bool = True
    duplication_enabled: bool = True
    architecture_check_enabled: bool = True


@dataclass
class BenchmarkingConfig:
    enabled: bool = True
    suite_enabled: bool = True
    historical_enabled: bool = True
    ranking_enabled: bool = True


@dataclass
class ReportsConfig:
    enabled: bool = True
    default_format: str = "markdown"
    export_path: str = "quality/reports"
    executive_enabled: bool = True


@dataclass
class ValidationConfig:
    enabled: bool = True
    production_gate_enabled: bool = True
    approval_required: bool = True
    min_quality_score: float = 0.8
    min_coverage: float = 0.75


@dataclass
class QualityConfig:
    """Top-level configuration for the Testing & Quality Engine."""

    environment: str = "development"
    debug: bool = False
    min_quality_score: float = 0.8

    testing: TestingConfig = field(default_factory=TestingConfig)
    unit: UnitConfig = field(default_factory=UnitConfig)
    integration: IntegrationConfig = field(default_factory=IntegrationConfig)
    regression: RegressionConfig = field(default_factory=RegressionConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    automation: AutomationConfig = field(default_factory=AutomationConfig)
    coverage: CoverageConfig = field(default_factory=CoverageConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    benchmarking: BenchmarkingConfig = field(default_factory=BenchmarkingConfig)
    reports: ReportsConfig = field(default_factory=ReportsConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)

    @classmethod
    def default(cls) -> QualityConfig:
        return cls()

    @classmethod
    def from_env(cls) -> QualityConfig:
        config = cls()
        config.environment = os.getenv("ENVIRONMENT", "development")
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.reports.export_path = os.getenv(
            "QUALITY_REPORTS_PATH", config.reports.export_path
        )
        return config


__all__ = [
    "TestingConfig", "UnitConfig", "IntegrationConfig", "RegressionConfig",
    "PerformanceConfig", "SecurityConfig", "AutomationConfig", "CoverageConfig",
    "AnalysisConfig", "BenchmarkingConfig", "ReportsConfig", "ValidationConfig",
    "QualityConfig",
]
