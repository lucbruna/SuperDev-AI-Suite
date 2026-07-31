"""Tests for reviews/ and approvals/ subsystems (Volume 26, Fase 6)."""

from __future__ import annotations

import pytest

from collaboration.collaboration_events import CollaborationEventType
from collaboration.collaboration_factory import build_engine
from collaboration.collaboration_models import (ApprovalStatus, EntityKind,
                                                MemberKind, MemberRole,
                                                ReviewKind, ReviewStatus)
from collaboration.approvals.approval_engine import ApprovalEngine
from collaboration.reviews.review_engine import ReviewEngine


@pytest.fixture
def engine():
    engine = build_engine()
    engine.attach_subsystem(
        "review_engine",
        ReviewEngine(events=engine.events, metrics=engine.metrics,
                     config=engine.config, security=engine.security,
                     registry=engine.registry))
    engine.attach_subsystem(
        "approval_engine",
        ApprovalEngine(events=engine.events, metrics=engine.metrics,
                       config=engine.config, security=engine.security,
                       registry=engine.registry))
    return engine


def _setup(engine):
    ws = engine.create_workspace("NEXUS ERP PROJECT", "SP-01")
    owner = engine.add_member(ws.workspace_id, "Carlos Diretor",
                              role=MemberRole.OWNER,
                              email="carlos@nexus.com.br")
    tech = engine.add_member(ws.workspace_id, "Ana Tech Lead",
                             role=MemberRole.ADMIN,
                             email="ana@nexus.com.br")
    dev = engine.add_member(ws.workspace_id, "Bruno Backend",
                            role=MemberRole.DEVELOPER,
                            email="bruno@nexus.com.br")
    security = engine.add_member(ws.workspace_id, "Lia Security",
                                 role=MemberRole.SECURITY,
                                 email="lia@nexus.com.br")
    project = engine.create_project(ws.workspace_id, "Sistema ERP")
    task = engine.create_task(project.project_id, ws.workspace_id,
                              "Criar aplicativo de vendas")
    return ws, owner, tech, dev, security, project, task


# ---------------------------------------------------------------- reviews ---

def test_review_creation(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    review = engine.review_engine.create(ReviewKind.CODE, task.task_id,
                                         tech.member_id)
    assert review.review_id.startswith("rev")
    assert review.target_kind == ReviewKind.CODE
    assert review.status == ReviewStatus.PENDING
    assert review.review_id in engine.review_engine.list()


def test_review_created_event(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    events = []
    engine.events.on(CollaborationEventType.REVIEW_CREATED, events.append)
    review = engine.review_engine.create(ReviewKind.CODE, task.task_id,
                                         tech.member_id)
    assert events and events[-1]["review_id"] == review.review_id


def test_review_decide(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    review = engine.review_engine.create(ReviewKind.CODE, task.task_id,
                                         tech.member_id)
    decided = engine.review_engine.decide(
        review.review_id, ReviewStatus.APPROVED, 85.0,
        [engine.review_engine.finding("minor", "ajustar comentário")])
    assert decided.status == ReviewStatus.APPROVED
    assert decided.score == 85.0
    assert len(decided.findings) == 1


def test_review_decided_event(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    review = engine.review_engine.create(ReviewKind.CODE, task.task_id,
                                         tech.member_id)
    events = []
    engine.events.on(CollaborationEventType.REVIEW_DECIDED, events.append)
    engine.review_engine.decide(review.review_id, ReviewStatus.REJECTED,
                                30.0, [])
    assert events and events[-1]["status"] == "rejected"


def test_review_auto_decision_security(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    review = engine.review_engine.create(ReviewKind.SECURITY, task.task_id,
                                         security.member_id)
    decided = engine.review_engine.decide_auto(
        review.review_id,
        [engine.review_engine.finding("critical",
                                      "SQL injection possível",
                                      "app/vendas.py:42")])
    assert decided.status == ReviewStatus.CHANGES_REQUESTED
    assert decided.score == 0.0


def test_review_auto_decision_clean(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    review = engine.review_engine.create(ReviewKind.CODE, task.task_id,
                                         tech.member_id)
    decided = engine.review_engine.decide_auto(review.review_id, [])
    assert decided.status == ReviewStatus.APPROVED
    assert decided.score == 100.0


def test_review_criteria_and_findings(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    checklist = engine.review_engine.checklist(ReviewKind.SECURITY)
    assert len(checklist) == 4
    from collaboration.reviews.review_findings import count_by_severity
    counts = count_by_severity([
        engine.review_engine.finding("major", "x"),
        engine.review_engine.finding("critical", "y"),
    ])
    assert counts["major"] == 1
    assert counts["critical"] == 1


def test_review_by_target(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    engine.review_engine.create(ReviewKind.CODE, task.task_id,
                                tech.member_id)
    reviews = engine.review_engine.by_target(task.task_id)
    assert len(reviews) == 1


# -------------------------------------------------------------- approvals ---

def test_approval_start(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    approval = engine.approval_engine.start(EntityKind.TASK, task.task_id,
                                            dev.member_id, flow="manager")
    assert approval.approval_id.startswith("appr")
    assert approval.status == ApprovalStatus.PENDING
    assert approval.flow == "manager"
    assert approval.approval_id in engine.approval_engine.list()


def test_approval_started_event(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    events = []
    engine.events.on(CollaborationEventType.APPROVAL_STARTED, events.append)
    approval = engine.approval_engine.start(EntityKind.TASK, task.task_id,
                                            dev.member_id)
    assert events and events[-1]["approval_id"] == approval.approval_id


def test_approval_single_step(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    approval = engine.approval_engine.start(EntityKind.TASK, task.task_id,
                                            dev.member_id, flow="manager")
    decided = engine.approval_engine.decide(approval.approval_id, True,
                                            tech.member_id)
    assert decided.status == ApprovalStatus.APPROVED
    assert decided.decided_by == tech.member_id


def test_approval_multi_step_flow(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    approval = engine.approval_engine.start(EntityKind.TASK, task.task_id,
                                            dev.member_id, flow="director")
    steps = engine.approval_engine.steps("director")
    assert [s["label"] for s in steps] == ["Developer", "Tech Lead",
                                           "Security", "Diretor"]
    engine.approval_engine.decide(approval.approval_id, True, dev.member_id)
    assert approval.status == ApprovalStatus.PENDING
    engine.approval_engine.decide(approval.approval_id, True,
                                  tech.member_id)
    engine.approval_engine.decide(approval.approval_id, True,
                                  security.member_id)
    decided = engine.approval_engine.decide(approval.approval_id, True,
                                            owner.member_id)
    assert decided.status == ApprovalStatus.APPROVED


def test_approval_rejected_at_step(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    approval = engine.approval_engine.start(EntityKind.TASK, task.task_id,
                                            dev.member_id, flow="director")
    engine.approval_engine.decide(approval.approval_id, True, dev.member_id)
    decided = engine.approval_engine.decide(approval.approval_id, False,
                                            tech.member_id,
                                            reason="arquitetura incorreta")
    assert decided.status == ApprovalStatus.REJECTED
    assert decided.reason == "arquitetura incorreta"


def test_approval_history(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    approval = engine.approval_engine.start(EntityKind.TASK, task.task_id,
                                            dev.member_id, flow="director")
    engine.approval_engine.decide(approval.approval_id, True, dev.member_id)
    engine.approval_engine.decide(approval.approval_id, True,
                                  tech.member_id)
    history = engine.approval_engine.history(approval.approval_id)
    assert history.count() == 2
    assert history.entries()[1]["decider"] == tech.member_id


def test_approval_cancel(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    approval = engine.approval_engine.start(EntityKind.TASK, task.task_id,
                                            dev.member_id)
    cancelled = engine.approval_engine.cancel(approval.approval_id,
                                              dev.member_id)
    assert cancelled.status == ApprovalStatus.CANCELLED


def test_approval_policy_agent_cannot_approve(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    agent = engine.add_agent(ws.workspace_id, "Planner IA")
    assert agent.kind == MemberKind.AGENT
    assert engine.approval_engine.can_approve(agent, EntityKind.TASK) is False
    assert engine.approval_engine.can_approve(tech, EntityKind.TASK) is True


def test_approval_policy_roles(engine):
    ws, owner, tech, dev, security, project, task = _setup(engine)
    roles = engine.approval_engine.roles("director")
    assert MemberRole.OWNER in roles
    assert MemberRole.SECURITY in roles
