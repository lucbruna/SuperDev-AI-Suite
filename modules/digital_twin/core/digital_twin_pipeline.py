"""Deterministic pipeline executing the twin lifecycle phases in order."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.config.constants import PHASES
from modules.digital_twin.core.digital_twin_context import DigitalTwinContext


@dataclass(slots=True)
class PipelineStepResult:
    """Outcome of a single pipeline phase."""

    phase: str
    status: str  # ran | skipped | failed
    detail: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"phase": self.phase, "status": self.status, "detail": self.detail}


@dataclass(slots=True)
class PipelineResult:
    """Aggregate result of a pipeline run."""

    steps: list[PipelineStepResult] = field(default_factory=list)

    def status(self) -> str:
        if any(s.status == "failed" for s in self.steps):
            return "failed"
        if any(s.status == "ran" for s in self.steps):
            return "ran"
        return "empty"

    def phases_run(self) -> list[str]:
        return [s.phase for s in self.steps if s.status == "ran"]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status(),
            "steps": [s.to_dict() for s in self.steps],
        }


class DigitalTwinPipeline:
    """Runs registered phase components in the canonical PHASES order."""

    def __init__(self, phases: tuple[str, ...] = PHASES) -> None:
        self._phases = phases

    @property
    def phases(self) -> tuple[str, ...]:
        return self._phases

    def run(self, ctx: DigitalTwinContext, *, skip_disabled: bool = True) -> PipelineResult:
        result = PipelineResult()
        config = ctx.config
        disabled = {
            "sync": not config.sync.enabled,
            "simulate": not config.simulation.enabled,
            "predict": not config.prediction.enabled,
            "monitor": not config.monitoring.enabled,
            "report": False,
        }
        for phase in self._phases:
            if skip_disabled and disabled.get(phase, False):
                result.steps.append(PipelineStepResult(phase, "skipped", "disabled by config"))
                continue
            if not ctx.registry.has(phase):
                result.steps.append(PipelineStepResult(phase, "skipped", "no component registered"))
                continue
            component = ctx.registry.get(phase)
            try:
                out = component(ctx)
            except Exception as exc:  # noqa: BLE001 - component isolation
                ctx.record(f"pipeline.{phase}.error", str(exc))
                result.steps.append(PipelineStepResult(phase, "failed", str(exc)))
                continue
            if out is not None:
                ctx.set_artifact(phase, out)
            ctx.record(f"pipeline.{phase}.ok", True)
            result.steps.append(PipelineStepResult(phase, "ran"))
        ctx.record("pipeline.status", result.status())
        return result
