"""Unit tests: governance package."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import (
    DECISION_APPROVED,
    DECISION_PENDING,
    DECISION_REJECTED,
    REC_APPROVED,
    REC_PENDING,
    REC_REJECTED,
    SEVERITY_CRITICAL,
    SEVERITY_INFO,
)
from modules.ai_evolution_engine.governance.approval_workflow import (
    ApprovalWorkflow,
)
from modules.ai_evolution_engine.governance.governance_engine import (
    GovernanceEngine,
)
from modules.ai_evolution_engine.tests.helpers import make_context, make_recommendation


def test_approval_workflow_auto_approves_low_severity():
    ctx = make_context()
    workflow = ApprovalWorkflow()
    item = make_recommendation(severity=SEVERITY_INFO)
    decision = workflow.submit(item, ctx)
    assert decision.status == DECISION_APPROVED
    assert workflow.pending_items() == []


def test_approval_workflow_holds_critical_for_operator():
    ctx = make_context()
    workflow = ApprovalWorkflow()
    item = make_recommendation(severity=SEVERITY_CRITICAL)
    decision = workflow.submit(item, ctx)
    assert decision.status == DECISION_PENDING
    assert len(workflow.pending_items()) == 1
    assert ctx.state.open_decisions == 1

    approved = workflow.approve(item, ctx)
    assert approved.status == DECISION_APPROVED
    assert ctx.state.open_decisions == 0


def test_governance_engine_routes_approval():
    ctx = make_context()
    governance = GovernanceEngine()
    item = make_recommendation(severity=SEVERITY_INFO)
    decision = governance.submit(item, ctx)
    assert decision.status == DECISION_APPROVED
    assert item.status == REC_APPROVED


def test_governance_engine_pending_then_approve():
    ctx = make_context()
    governance = GovernanceEngine()
    item = make_recommendation(severity=SEVERITY_CRITICAL)
    decision = governance.submit(item, ctx)
    assert decision.status == DECISION_PENDING
    assert item.status == REC_PENDING

    final = governance.approve(item, ctx)
    assert final.status == DECISION_APPROVED
    assert item.status == REC_APPROVED


def test_governance_engine_reject():
    ctx = make_context()
    governance = GovernanceEngine()
    item = make_recommendation(severity=SEVERITY_CRITICAL)
    governance.submit(item, ctx)
    final = governance.reject(item, ctx)
    assert final.status == DECISION_REJECTED
    assert item.status == REC_REJECTED
