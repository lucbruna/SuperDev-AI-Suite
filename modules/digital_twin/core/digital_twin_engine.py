"""Digital Twin engine: orchestrates a full lifecycle cycle."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.core.digital_twin_context import DigitalTwinContext
from modules.digital_twin.core.digital_twin_pipeline import (
    DigitalTwinPipeline,
    PipelineResult,
)


@dataclass(slots=True)
class EngineResult:
    """Outcome of a single engine cycle."""

    pipeline: PipelineResult = field(default_factory=PipelineResult)
    cycle: int = 0
    event_sequence: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "cycle": self.cycle,
            "pipeline": self.pipeline.to_dict(),
            "event_sequence": self.event_sequence,
        }


class DigitalTwinEngine:
    """Runs the pipeline once and publishes lifecycle events."""

    def __init__(self, pipeline: DigitalTwinPipeline | None = None) -> None:
        self._pipeline = pipeline or DigitalTwinPipeline()
        self._cycles = 0

    @property
    def cycles(self) -> int:
        return self._cycles

    def run(self, ctx: DigitalTwinContext) -> EngineResult:
        self._cycles += 1
        pipeline_result = self._pipeline.run(ctx)
        ctx.publish(
            "cycle.completed",
            {
                "cycle": self._cycles,
                "status": pipeline_result.status(),
                "phases": pipeline_result.phases_run(),
            },
        )
        ctx.record("engine.cycles", self._cycles)
        return EngineResult(
            pipeline=pipeline_result,
            cycle=self._cycles,
            event_sequence=ctx.events.last_sequence,
        )
