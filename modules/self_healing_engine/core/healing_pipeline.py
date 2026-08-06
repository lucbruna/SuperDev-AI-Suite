"""Healing pipeline: diagnose, plan, validate, approve, repair, verify, recover."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.self_healing_engine.config.constants import (
    PHASE_APPROVE,
    PHASE_DIAGNOSE,
    PHASE_PLAN,
    PHASE_RECOVER,
    PHASE_REPAIR,
    PHASE_REPORT,
    PHASE_VALIDATE,
    PHASE_VERIFY,
    REPAIR_SUCCEEDED,
)
from modules.self_healing_engine.core.healing_context import HealingContext
from modules.self_healing_engine.diagnostics.health import HealthScore
from modules.self_healing_engine.monitoring.health_monitor import HealthMonitor
from modules.self_healing_engine.recovery.rollback import RollbackManager
from modules.self_healing_engine.recovery.snapshot import SnapshotManager
from modules.self_healing_engine.repair.executor import (
    RepairExecutor,
    RepairOutcome,
)
from modules.self_healing_engine.repair.planner import (
    HealingRepairError,
    RepairPlan,
    RepairPlanner,
)
from modules.self_healing_engine.validation.validators import ValidatorRunner

_STATUS_OK = "ok"
_STATUS_NEEDS_APPROVAL = "needs_approval"
_STATUS_FAILED = "failed"


@dataclass(slots=True)
class PipelineStepResult:
    """Outcome of a single pipeline phase."""

    phase: str
    ok: bool
    detail: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {"phase": self.phase, "ok": self.ok, "detail": self.detail}


@dataclass(slots=True)
class PipelineResult:
    """Aggregated outcome of a healing pipeline run."""

    steps: list[PipelineStepResult] = field(default_factory=list)
    status: str = _STATUS_OK
    plan: RepairPlan | None = None
    outcome: RepairOutcome | None = None
    health: HealthScore | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status,
            "plan": self.plan.to_dict() if self.plan else None,
            "outcome": self.outcome.to_dict() if self.outcome else None,
            "health": self.health.to_dict() if self.health else None,
        }

    def phases_run(self) -> list[str]:
        return [s.phase for s in self.steps]


class HealingPipeline:
    """Runs a full healing cycle through the phase pipeline."""

    def __init__(
        self,
        monitor: HealthMonitor | None = None,
        planner: RepairPlanner | None = None,
        validator: ValidatorRunner | None = None,
        executor: RepairExecutor | None = None,
        snapshots: SnapshotManager | None = None,
        rollback: RollbackManager | None = None,
    ) -> None:
        self._monitor = monitor or HealthMonitor()
        self._planner = planner or RepairPlanner()
        self._validator = validator or ValidatorRunner()
        self._executor = executor or RepairExecutor()
        self._snapshots = snapshots or SnapshotManager()
        self._rollback = rollback or RollbackManager(self._snapshots)

    def run(
        self,
        ctx: HealingContext,
        incident: dict[str, object] | None = None,
    ) -> PipelineResult:
        result = PipelineResult()

        score = self._monitor.run(ctx)
        result.health = score
        result.steps.append(
            PipelineStepResult(
                phase=PHASE_DIAGNOSE,
                ok=True,
                detail={"score": score.score, "status": score.status},
            )
        )

        if incident:
            result = self._run_incident(ctx, result, incident)

        result.steps.append(
            PipelineStepResult(
                phase=PHASE_REPORT,
                ok=result.status != _STATUS_FAILED,
                detail={"status": result.status},
            )
        )
        ctx.publish("pipeline.completed", {"status": result.status})
        return result

    def _run_incident(
        self,
        ctx: HealingContext,
        result: PipelineResult,
        incident: dict[str, object],
    ) -> PipelineResult:
        kind = str(incident.get("kind", ""))
        target = str(incident.get("target", ""))
        raw_impact = incident.get("impact_score", 0)
        impact = int(raw_impact) if isinstance(raw_impact, (int, float)) else 0
        description = str(incident.get("description", ""))

        try:
            plan = self._planner.plan(
                kind, target, ctx, impact_score=impact, description=description
            )
        except HealingRepairError as exc:
            result.status = _STATUS_FAILED
            result.steps.append(
                PipelineStepResult(
                    phase=PHASE_PLAN, ok=False, detail={"error": str(exc)}
                )
            )
            return result
        result.plan = plan
        result.steps.append(
            PipelineStepResult(
                phase=PHASE_PLAN,
                ok=True,
                detail={
                    "kind": plan.kind,
                    "target": plan.target,
                    "risk": plan.risk,
                },
            )
        )

        validation = self._validator.run(plan.target, ctx)
        failed = [v for v in validation if not v.passed]
        result.steps.append(
            PipelineStepResult(
                phase=PHASE_VALIDATE,
                ok=not failed,
                detail={"passed": len(validation) - len(failed), "failed": len(failed)},
            )
        )
        if failed:
            result.status = _STATUS_FAILED
            return result

        if plan.requires_approval:
            result.status = _STATUS_NEEDS_APPROVAL
            result.steps.append(
                PipelineStepResult(
                    phase=PHASE_APPROVE,
                    ok=False,
                    detail={"message": "approval required"},
                )
            )
            ctx.publish("pipeline.approval_required", {"plan": plan.to_dict()})
            return result
        result.steps.append(
            PipelineStepResult(phase=PHASE_APPROVE, ok=True, detail={"auto": True})
        )

        before_score = _diagnosed_score(result)
        self._snapshots.create(
            "pre_repair", ctx, {"kind": plan.kind, "target": plan.target}
        )
        outcome = self._executor.execute(plan, ctx)
        result.outcome = outcome
        result.steps.append(
            PipelineStepResult(
                phase=PHASE_REPAIR,
                ok=outcome.status == REPAIR_SUCCEEDED,
                detail=outcome.to_dict(),
            )
        )

        verify_score = self._monitor.run(ctx)
        result.health = verify_score
        verify_ok = verify_score.score >= before_score
        result.steps.append(
            PipelineStepResult(
                phase=PHASE_VERIFY,
                ok=verify_ok,
                detail={"score": verify_score.score, "status": verify_score.status},
            )
        )

        if outcome.status == REPAIR_SUCCEEDED and verify_ok:
            result.status = _STATUS_OK
        else:
            result.status = _STATUS_FAILED
            self._rollback.rollback_latest(ctx, "pre_repair")
            result.steps.append(
                PipelineStepResult(
                    phase=PHASE_RECOVER,
                    ok=True,
                    detail={"message": "rolled back failed repair"},
                )
            )
        return result


def _diagnosed_score(result: PipelineResult) -> float:
    """Return the pre-repair health score recorded during diagnosis."""
    for step in result.steps:
        if step.phase == PHASE_DIAGNOSE:
            detail = step.detail.get("score", 0.0)
            return float(detail) if isinstance(detail, (int, float)) else 0.0
    return 0.0
