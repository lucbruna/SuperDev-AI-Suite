"""Tests for the healing pipeline: end-to-end phase behaviour."""
from __future__ import annotations

from modules.self_healing_engine.config.constants import (
    PHASE_APPROVE,
    PHASE_DIAGNOSE,
    PHASE_PLAN,
    PHASE_REPAIR,
    PHASE_REPORT,
    PHASE_VALIDATE,
    PHASE_VERIFY,
)
from modules.self_healing_engine.core import HealingPipeline
from modules.self_healing_engine.tests.helpers import make_context


def _incident(kind: str = "dependency", target: str = "requirements.txt",
              impact: int = 0) -> dict[str, object]:
    return {"kind": kind, "target": target, "impact_score": impact}


def test_pipeline_healthy_cycle_without_incident() -> None:
    ctx = make_context()
    result = HealingPipeline().run(ctx)

    assert result.status == "ok"
    assert result.phases_run() == [PHASE_DIAGNOSE, PHASE_REPORT]
    assert result.health is not None


def test_pipeline_auto_repair_runs_all_phases() -> None:
    ctx = make_context()
    result = HealingPipeline().run(ctx, _incident(impact=0))

    assert result.status == "ok"
    assert result.phases_run() == [
        PHASE_DIAGNOSE, PHASE_PLAN, PHASE_VALIDATE, PHASE_APPROVE,
        PHASE_REPAIR, PHASE_VERIFY, PHASE_REPORT,
    ]
    assert result.outcome is not None
    assert result.outcome.status == "succeeded"


def test_pipeline_requires_approval_for_medium_impact() -> None:
    ctx = make_context()
    result = HealingPipeline().run(ctx, _incident(impact=10))

    assert result.status == "needs_approval"
    assert PHASE_REPAIR not in result.phases_run()


def test_pipeline_fails_on_disallowed_kind() -> None:
    ctx = make_context()
    result = HealingPipeline().run(ctx, _incident(kind="unknown", target="x", impact=0))

    assert result.status == "failed"
    assert result.phases_run() == [PHASE_DIAGNOSE, PHASE_PLAN, PHASE_REPORT]


def test_pipeline_fails_on_validation_gate(tmp_path) -> None:
    ctx = make_context(tmp_path)
    # Target inexistente -> SyntaxValidator falha -> gate de validação
    result = HealingPipeline().run(
        ctx, _incident(target="missing.py", impact=0)
    )

    assert result.status == "failed"
    assert PHASE_REPAIR not in result.phases_run()
    assert PHASE_VALIDATE in result.phases_run()
