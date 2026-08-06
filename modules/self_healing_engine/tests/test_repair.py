"""Tests for repair: planner risk assessment and executor policies."""
from __future__ import annotations

import pytest

from modules.self_healing_engine.config.constants import (
    REPAIR_APPROVED,
    REPAIR_PENDING,
    REPAIR_ROLLED_BACK,
    REPAIR_SKIPPED,
    REPAIR_SUCCEEDED,
)
from modules.self_healing_engine.repair import (
    HealingRepairError,
    RepairExecutor,
    RepairPlanner,
)
from modules.self_healing_engine.tests.helpers import make_context


def test_planner_low_impact_auto_approved() -> None:
    ctx = make_context()
    planner = RepairPlanner()
    plan = planner.plan("dependency", "requirements.txt", ctx, impact_score=0)

    assert plan.risk == "low"
    assert plan.requires_approval is False
    assert plan.steps == ["repair:dependency:requirements.txt"]


def test_planner_medium_impact_requires_approval() -> None:
    ctx = make_context()
    planner = RepairPlanner()
    plan = planner.plan("dependency", "requirements.txt", ctx, impact_score=10)

    assert plan.risk == "medium"
    assert plan.requires_approval is True


def test_planner_rejects_disallowed_kind() -> None:
    ctx = make_context()
    from modules.self_healing_engine.config.repair_rules import RepairRulesConfig

    planner = RepairPlanner(rules=RepairRulesConfig(allowed_repair_kinds=("dependency",)))
    with pytest.raises(HealingRepairError):
        planner.plan("api", "some/path", ctx)


def test_planner_rejects_protected_path() -> None:
    ctx = make_context()
    planner = RepairPlanner()
    with pytest.raises(HealingRepairError):
        planner.plan("dependency", ".superdev/config.json", ctx)


def test_executor_runs_approved_plan() -> None:
    ctx = make_context()
    planner = RepairPlanner()
    executor = RepairExecutor()

    plan = planner.plan("dependency", "requirements.txt", ctx, impact_score=0)
    outcome = executor.execute(plan, ctx)

    assert outcome.status == REPAIR_SUCCEEDED
    assert outcome.attempts == 1
    assert ctx.memory.has("repair:requirements.txt")


def test_executor_waits_for_approval() -> None:
    ctx = make_context()
    planner = RepairPlanner()
    executor = RepairExecutor()

    plan = planner.plan("dependency", "requirements.txt", ctx, impact_score=10)
    outcome = executor.execute(plan, ctx)

    assert outcome.status == REPAIR_PENDING
    assert "approval" in outcome.message


def test_executor_approve_and_rollback() -> None:
    ctx = make_context()
    planner = RepairPlanner()
    executor = RepairExecutor()

    plan = planner.plan("dependency", "requirements.txt", ctx, impact_score=10)
    approved = executor.approve(plan, ctx)
    rolled = executor.rollback(plan, ctx)

    assert approved.status == REPAIR_APPROVED
    assert rolled.status == REPAIR_ROLLED_BACK
    assert rolled.rolled_back is True
