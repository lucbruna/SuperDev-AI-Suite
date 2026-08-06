"""Self-Healing Engine engine: orchestrates one healing cycle."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.self_healing_engine.core.healing_context import HealingContext
from modules.self_healing_engine.core.healing_pipeline import (
    HealingPipeline,
    PipelineResult,
)


@dataclass(slots=True)
class EngineResult:
    """Outcome of a single healing engine cycle."""

    pipeline: PipelineResult = field(default_factory=PipelineResult)
    cycle: int = 0
    event_sequence: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "cycle": self.cycle,
            "pipeline": self.pipeline.to_dict(),
            "event_sequence": self.event_sequence,
        }


class HealingEngine:
    """Runs the healing pipeline once and publishes lifecycle events."""

    def __init__(self, pipeline: HealingPipeline | None = None) -> None:
        self._pipeline = pipeline or HealingPipeline()
        self._cycles = 0

    @property
    def cycles(self) -> int:
        return self._cycles

    @property
    def pipeline(self) -> HealingPipeline:
        return self._pipeline

    def run(
        self, ctx: HealingContext, incident: dict[str, object] | None = None
    ) -> EngineResult:
        self._cycles += 1
        pipeline_result = self._pipeline.run(ctx, incident)
        ctx.publish(
            "cycle.completed",
            {
                "cycle": self._cycles,
                "status": pipeline_result.status,
                "phases": pipeline_result.phases_run(),
            },
        )
        ctx.record("engine.cycles", self._cycles)
        return EngineResult(
            pipeline=pipeline_result,
            cycle=self._cycles,
            event_sequence=ctx.events.last_sequence,
        )
