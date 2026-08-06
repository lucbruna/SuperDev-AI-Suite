"""Benchmark runner: deterministic performance snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class BenchmarkResult:
    """A single deterministic benchmark measurement."""

    metric: str
    value: float
    unit: str
    previous_value: float | None = None
    delta: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "metric": self.metric,
            "value": self.value,
            "unit": self.unit,
            "previous_value": self.previous_value,
            "delta": self.delta,
        }


class BenchmarkRunner:
    """Measures metrics from context artifacts and compares to baseline."""

    def __init__(self, baseline: dict[str, float] | None = None) -> None:
        self._baseline: dict[str, float] = dict(baseline or {})

    def run(self, ctx: EvolutionContext, metrics: list[str]) -> list[BenchmarkResult]:
        results: list[BenchmarkResult] = []
        for metric in metrics:
            value = float(ctx.get_artifact(metric, 0.0) or 0.0)
            previous = self._baseline.get(metric)
            delta = value - previous if previous is not None else 0.0
            results.append(
                BenchmarkResult(
                    metric=metric,
                    value=value,
                    unit="ratio",
                    previous_value=previous,
                    delta=round(delta, 6),
                )
            )
            self._baseline[metric] = value
        return results
