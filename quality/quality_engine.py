from __future__ import annotations

from typing import Any

from .analysis.analyzer_engine import AnalyzerEngine
from .automation.automation_engine import AutomationEngine
from .benchmarking.benchmark_engine import BenchmarkEngine
from .coverage.coverage_engine import CoverageEngine
from .integration.integration_engine import IntegrationEngine
from .performance.performance_engine import PerformanceEngine
from .quality_config import QualityConfig
from .quality_context import QualityContext
from .quality_events import QualityEventBus
from .quality_logger import QualityLogger
from .quality_metrics import QualityMetrics
from .quality_registry import QualityRegistry
from .quality_runtime import QualityRuntime
from .quality_security import QualitySecurity
from .regression.regression_engine import RegressionEngine
from .reports.report_engine import QualityReportEngine
from .security.security_test_engine import SecurityTestEngine
from .testing.testing_engine import TestingEngine
from .unit.unit_test_engine import UnitTestEngine
from .validation.validation_engine import ValidationEngine


class QualityEngine:
    """Central orchestrator for the Testing & Quality Engine.

    Owns and coordinates all 12 subsystems:
    testing → unit → integration → regression → performance → security →
    automation → coverage → analysis → benchmarking → reports → validation,
    ending in a production gate that approves or blocks deliveries.
    """

    def __init__(self, config: QualityConfig | None = None) -> None:
        self._config = config or QualityConfig.default()
        self._event_bus = QualityEventBus()
        self._logger = QualityLogger(name="quality-engine")
        self._metrics = QualityMetrics()
        self._registry = QualityRegistry()
        self._runtime = QualityRuntime()
        self._security = QualitySecurity()
        self._context = QualityContext()
        self._running = False

        # Subsystems
        self.testing = TestingEngine(self)
        self.unit = UnitTestEngine(self)
        self.integration = IntegrationEngine(self)
        self.regression = RegressionEngine(self)
        self.performance = PerformanceEngine(self)
        self.security = SecurityTestEngine(self)
        self.automation = AutomationEngine(self)
        self.coverage = CoverageEngine(self)
        self.analysis = AnalyzerEngine(self)
        self.benchmarking = BenchmarkEngine(self)
        self.reports = QualityReportEngine(self)
        self.validation = ValidationEngine(self)

    # -- lifecycle -----------------------------------------------------------

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._runtime.start()
        for subsystem in self._subsystems():
            await subsystem.initialize()
        await self._event_bus.emit("quality.engine.started", {"config": self._config})
        self._logger.info("QualityEngine started")

    async def stop(self) -> None:
        if not self._running:
            return
        for subsystem in self._subsystems():
            await subsystem.shutdown()
        self._running = False
        await self._event_bus.emit("quality.engine.stopped", {})
        self._logger.info("QualityEngine stopped")

    def _subsystems(self) -> list[Any]:
        return [
            self.testing, self.unit, self.integration, self.regression,
            self.performance, self.security, self.automation, self.coverage,
            self.analysis, self.benchmarking, self.reports, self.validation,
        ]

    # -- high-level flows ----------------------------------------------------

    async def run_full_testing(
        self,
        target: str,
        source: str | None = None,
    ) -> dict[str, Any]:
        """End-to-end: generate unit tests → run → analyze → score → report."""
        suite = self.unit.generate_suite(target, source=source)
        result = await self.testing.run_suite(suite)
        coverage = self.coverage.measure(target, {"covered_lines": 0, "total_lines": 100})
        analysis = self.analysis.analyze_code(target, source or "")
        score = self.compute_score(
            target,
            code=analysis.get("quality", 0.0),
            tests=result.passed_rate,
            security=1.0,
            performance=1.0,
            documentation=0.9,
        )
        report_id = await self.reports.create_quality_report(target, score, result)
        return {
            "suite_id": suite.suite_id,
            "result": result,
            "coverage": coverage,
            "analysis": analysis,
            "score": score,
            "report_id": report_id,
        }

    def compute_score(
        self,
        target: str,
        code: float = 0.0,
        tests: float = 0.0,
        security: float = 0.0,
        performance: float = 0.0,
        documentation: float = 0.0,
    ) -> dict[str, Any]:
        """Compute the composite Quality Score (code/tests/security/performance/docs)."""
        score = self.analysis.score(
            target,
            code=code,
            tests=tests,
            security=security,
            performance=performance,
            documentation=documentation,
        )
        self._metrics.gauge("quality.score", score.overall, labels={"target": target})
        return {
            "target": score.target,
            "code": score.code,
            "tests": score.tests,
            "security": score.security,
            "performance": score.performance,
            "documentation": score.documentation,
            "overall": score.overall,
        }

    async def evaluate_production_gate(self, target: str, signals: dict[str, Any]) -> dict[str, Any]:
        """Validate a delivery against the production gate."""
        gate = await self.validation.evaluate_gate(target, signals)
        await self._event_bus.emit("quality.gate.evaluated", {
            "gate_id": gate.gate_id,
            "target": target,
            "decision": gate.decision.value,
        })
        self._metrics.increment(
            "quality.gates", labels={"decision": gate.decision.value}
        )
        return {
            "gate_id": gate.gate_id,
            "target": gate.target,
            "decision": gate.decision.value,
            "quality_score": gate.quality_score,
            "blocked_reasons": gate.blocked_reasons,
            "checks": gate.checks,
        }

    # -- status --------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "subsystems": {
                s.__class__.__name__: s.status()
                for s in self._subsystems()
            },
            "runtime": self._runtime.snapshot(),
            "registry_size": self._registry.size,
            "metrics": self._metrics.snapshot(),
        }

    async def health(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "uptime": self._runtime.uptime,
            "subsystems_initialized": sum(
                1 for s in self._subsystems() if s.status().get("initialized")
            ),
            "config": {
                "testing": self._config.testing.enabled,
                "unit": self._config.unit.enabled,
                "integration": self._config.integration.enabled,
                "regression": self._config.regression.enabled,
                "performance": self._config.performance.enabled,
                "security": self._config.security.enabled,
                "automation": self._config.automation.enabled,
                "coverage": self._config.coverage.enabled,
                "analysis": self._config.analysis.enabled,
                "benchmarking": self._config.benchmarking.enabled,
                "reports": self._config.reports.enabled,
                "validation": self._config.validation.enabled,
            },
        }

    # -- accessors -----------------------------------------------------------

    @property
    def config(self) -> QualityConfig:
        return self._config

    @property
    def event_bus(self) -> QualityEventBus:
        return self._event_bus

    @property
    def logger(self) -> QualityLogger:
        return self._logger

    @property
    def metrics(self) -> QualityMetrics:
        return self._metrics

    @property
    def registry(self) -> QualityRegistry:
        return self._registry

    @property
    def runtime(self) -> QualityRuntime:
        return self._runtime

    @property
    def security_guard(self) -> QualitySecurity:
        return self._security

    @property
    def context(self) -> QualityContext:
        return self._context

    @property
    def is_running(self) -> bool:
        return self._running


__all__ = ["QualityEngine"]
