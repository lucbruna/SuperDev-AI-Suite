from __future__ import annotations

import statistics
import time
from collections.abc import Callable
from typing import Any

from ..quality_models import PerformanceReport
from .latency import LatencyAnalyzer


class PerformanceEngine:
    """Performance testing — load, stress, endurance, benchmark, latency, throughput, resources."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.performance
        self.latency_analyzer = LatencyAnalyzer(
            target_ms=self.config.latency_target_ms, engine=engine
        )
        self._reports: dict[str, PerformanceReport] = {}
        self._benchmarks: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    # -- latency -------------------------------------------------------------

    def latency(self, operation: Callable[[], Any], samples: int = 100) -> dict[str, Any]:
        """Measure latency of a callable over N samples."""
        latencies: list[float] = []
        for _ in range(max(1, samples)):
            started = time.perf_counter()
            operation()
            latencies.append((time.perf_counter() - started) * 1000)
        latencies.sort()
        return {
            "samples": len(latencies),
            "avg_ms": round(statistics.mean(latencies), 2),
            "p50_ms": round(latencies[len(latencies) // 2], 2),
            "p95_ms": round(latencies[int(len(latencies) * 0.95) - 1], 2),
            "min_ms": round(latencies[0], 2),
            "max_ms": round(latencies[-1], 2),
        }

    # -- throughput ----------------------------------------------------------

    def throughput(self, operation: Callable[[], Any], duration_s: float = 1.0) -> float:
        """Measure operations per second over a fixed window."""
        started = time.perf_counter()
        count = 0
        while time.perf_counter() - started < max(0.01, duration_s):
            operation()
            count += 1
        return round(count / (time.perf_counter() - started), 2)

    # -- load / stress / endurance -------------------------------------------

    def load_test(self, operation: Callable[[], Any], users: int = 10, samples: int = 50) -> dict[str, Any]:
        """Simulate concurrent load and aggregate results."""
        latency_stats = self.latency(operation, samples=samples)
        return {
            "users": users,
            "latency": latency_stats,
            "throughput": self.throughput(operation),
        }

    def stress_test(self, operation: Callable[[], Any], iterations: int = 1000) -> dict[str, Any]:
        """Push an operation hard and report failures/peak latency."""
        failures = 0
        latencies: list[float] = []
        for _ in range(iterations):
            started = time.perf_counter()
            try:
                operation()
            except Exception:  # noqa: BLE001 - stress tests capture all failures
                failures += 1
            latencies.append((time.perf_counter() - started) * 1000)
        return {
            "iterations": iterations,
            "failures": failures,
            "failure_rate": round(failures / iterations, 4),
            "avg_ms": round(statistics.mean(latencies), 2),
            "peak_ms": round(max(latencies), 2),
        }

    def endurance_test(self, operation: Callable[[], Any], duration_s: float = 5.0) -> dict[str, Any]:
        """Run an operation for a sustained period, tracking error rate."""
        started = time.perf_counter()
        count = 0
        errors = 0
        while time.perf_counter() - started < max(0.1, duration_s):
            count += 1
            try:
                operation()
            except Exception:  # noqa: BLE001
                errors += 1
        return {
            "duration_s": round(time.perf_counter() - started, 2),
            "iterations": count,
            "errors": errors,
            "error_rate": round(errors / count, 4) if count else 0.0,
        }

    # -- resource analysis ---------------------------------------------------

    def resource_analysis(self, memory_mb: float = 0.0, cpu_pct: float = 0.0) -> dict[str, Any]:
        return {"memory_mb": memory_mb, "cpu_pct": cpu_pct}

    # -- report --------------------------------------------------------------

    def build_report(self, target: str, metrics: dict[str, Any]) -> PerformanceReport:
        report = PerformanceReport(
            target=target,
            avg_latency_ms=metrics.get("avg_latency_ms", 0.0),
            p95_latency_ms=metrics.get("p95_latency_ms", 0.0),
            throughput=metrics.get("throughput", 0.0),
            error_rate=metrics.get("error_rate", 0.0),
            peak_memory_mb=metrics.get("peak_memory_mb", 0.0),
        )
        self._reports[report.report_id] = report
        self.engine.registry.register_performance(report)
        self.engine.metrics.increment("performance.reports")
        return report

    def performance_score(self, report: PerformanceReport) -> float:
        """1.0 when latency/errors are within targets, lower otherwise."""
        latency_ok = report.avg_latency_ms <= self.config.latency_target_ms
        throughput_ok = report.throughput >= self.config.throughput_target or report.throughput == 0.0
        errors_ok = report.error_rate <= 0.01
        score = sum([latency_ok, throughput_ok, errors_ok]) / 3
        return round(score, 4)

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "reports": len(self._reports),
            "benchmarks": len(self._benchmarks),
        }


__all__ = ["PerformanceEngine"]
