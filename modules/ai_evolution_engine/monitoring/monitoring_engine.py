"""Monitoring engine: deterministic health/status reporting."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.core.evolution_context import EvolutionContext


@dataclass(slots=True)
class MetricSample:
    """A single deterministic metric sample."""

    name: str
    value: float

    def to_dict(self) -> dict[str, object]:
        return {"name": self.name, "value": self.value}


@dataclass(slots=True)
class HealthSnapshot:
    """A deterministic health summary of the engine pipeline."""

    healthy: bool = True
    issues: list[str] = field(default_factory=list)
    samples: list[MetricSample] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "healthy": self.healthy,
            "issues": list(self.issues),
            "samples": [s.to_dict() for s in self.samples],
        }


class MonitoringEngine:
    """Collects metrics and derives a health snapshot."""

    def __init__(self) -> None:
        self._history: list[dict[str, float]] = []

    def collect(self, ctx: EvolutionContext) -> HealthSnapshot:
        samples: list[MetricSample] = []
        issues: list[str] = []
        for name, threshold in (
            ("cache_hit_ratio", 0.8),
            ("test_pass_rate", 0.9),
            ("resource_usage_ratio", 0.85),
        ):
            value = float(ctx.get_artifact(name, 1.0) or 1.0)
            samples.append(MetricSample(name=name, value=round(value, 4)))
            if name == "resource_usage_ratio":
                if value >= threshold:
                    issues.append(f"{name} above threshold {threshold}")
            elif value < threshold:
                issues.append(f"{name} below threshold {threshold}")
        snapshot = HealthSnapshot(healthy=not issues, issues=issues, samples=samples)
        self._history.append(
            {sample.name: sample.value for sample in samples}
        )
        if len(self._history) > 1000:
            self._history = self._history[-500:]
        return snapshot

    def history(self) -> list[dict[str, float]]:
        return list(self._history)
