"""Benchmark suite: named collections of metrics."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.benchmarking.benchmark_runner import (
    BenchmarkResult,
    BenchmarkRunner,
)
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class BenchmarkSuite:
    """A named, deterministic metric bundle."""

    name: str
    metrics: tuple[str, ...] = field(default_factory=tuple)

    def run(self, ctx: EvolutionContext, runner: BenchmarkRunner) -> dict[str, BenchmarkResult]:
        return {
            metric: result
            for metric, result in zip(
                self.metrics, runner.run(ctx, list(self.metrics))
            )
        }


DEFAULT_SUITE = BenchmarkSuite(
    name="default",
    metrics=(
        "cache_hit_ratio",
        "test_pass_rate",
        "duplicate_dependencies",
        "p95_latency_ms",
        "resource_usage_ratio",
    ),
)
