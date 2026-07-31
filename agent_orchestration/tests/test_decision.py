"""Tests for the decision/ subpackage (Volume 31, Fase 4)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.decision import (ApprovalManager, DecisionEngine,
                                          PriorityManager, RiskAnalyzer,
                                          RuleEngine)
from agent_orchestration.orchestrator_events import OrchestratorEventType
from agent_orchestration.orchestrator_models import (AgentTask, Priority,
                                                     RiskLevel, TaskStatus)


def _task(task_id: str, **kwargs: Any) -> AgentTask:
    defaults: dict[str, Any] = {"title": f"Tarefa {task_id}"}
    defaults.update(kwargs)
    return AgentTask(task_id=task_id, **defaults)


class TestRuleEngine:
    def test_rules_fire_in_order(self):
        engine = RuleEngine()
        engine.add_rule("low", lambda ctx: ctx["score"] < 50,
                        lambda ctx: "low_action")
        engine.add_rule("high", lambda ctx: ctx["score"] >= 50,
                        lambda ctx: "high_action")
        fired = engine.evaluate({"score": 80})
        assert [entry["rule"] for entry in fired] == ["high"]
        assert fired[0]["result"] == "high_action"

    def test_error_isolation(self):
        engine = RuleEngine()

        def bad(ctx):
            raise ValueError("rule boom")

        engine.add_rule("bad", lambda ctx: True, bad)
        fired = engine.evaluate({})
        assert fired[0]["ok"] is False
        assert "rule boom" in fired[0]["error"]

    def test_names(self):
        engine = RuleEngine()
        engine.add_rule("a", lambda ctx: True, lambda ctx: 1)
        engine.add_rule("b", lambda ctx: False, lambda ctx: 2)
        assert engine.names() == ["a", "b"]
        assert engine.count() == 2


class TestPriorityManager:
    def test_from_score_bands(self):
        assert PriorityManager.from_score(0.1) == Priority.LOW
        assert PriorityManager.from_score(0.3) == Priority.MEDIUM
        assert PriorityManager.from_score(0.6) == Priority.HIGH
        assert PriorityManager.from_score(0.9) == Priority.CRITICAL

    def test_decide_sets_task(self):
        task = _task("t1")
        priority = PriorityManager().decide(task, 0.9)
        assert task.priority == Priority.CRITICAL
        assert priority == Priority.CRITICAL

    def test_rank_and_sort(self):
        assert PriorityManager.rank(Priority.HIGH) == 2
        tasks = [_task("low", priority=Priority.LOW),
                 _task("high", priority=Priority.HIGH),
                 _task("med", priority=Priority.MEDIUM)]
        ordered = PriorityManager.sort(tasks)
        assert [task.task_id for task in ordered] == ["high", "med", "low"]


class TestRiskAnalyzer:
    def test_baseline_low(self):
        report = RiskAnalyzer().assess(_task("t1"))
        assert report["level"] == RiskLevel.LOW
        assert report["reasons"] == []

    def test_approval_and_retry_raise_risk(self):
        report = RiskAnalyzer().assess(
            _task("t2", approval_required=True, attempts=2,
                  risk_level=RiskLevel.MEDIUM))
        assert report["level"] == RiskLevel.HIGH
        assert "retrying" in report["reasons"]

    def test_broad_permissions(self):
        report = RiskAnalyzer().assess(
            _task("t3", risk_level=RiskLevel.HIGH), permissions=["*"])
        assert report["level"] == RiskLevel.CRITICAL

    def test_max_risk_caps(self):
        report = RiskAnalyzer().assess(
            _task("t4", risk_level=RiskLevel.CRITICAL),
            permissions=["*"])
        assert report["level"] == RiskLevel.CRITICAL


class TestApprovalManager:
    def test_require_marks_pending(self):
        approvals = ApprovalManager()
        task = _task("t1")
        approvals.require(task, "high impact")
        assert task.status == TaskStatus.APPROVAL_REQUIRED
        assert task.approval_required is True
        assert approvals.is_pending("t1") is True
        assert approvals.pending()[0]["reason"] == "high impact"

    def test_resolve_approved_queues(self):
        approvals = ApprovalManager()
        task = _task("t1")
        approvals.require(task)
        assert approvals.resolve(task, True, "human") is True
        assert task.status == TaskStatus.QUEUED
        assert approvals.is_pending("t1") is False

    def test_resolve_rejected_cancels(self):
        approvals = ApprovalManager()
        task = _task("t1")
        approvals.require(task)
        approvals.resolve(task, False)
        assert task.status == TaskStatus.CANCELLED

    def test_resolve_unknown_fails(self):
        approvals = ApprovalManager()
        assert approvals.resolve(_task("nope"), True) is False

    def test_events_published(self):
        events = []
        approvals = ApprovalManager()
        approvals.events.on(OrchestratorEventType.APPROVAL_REQUIRED,
                            lambda payload: events.append("required"))
        approvals.events.on(OrchestratorEventType.APPROVAL_RESOLVED,
                            lambda payload: events.append("resolved"))
        task = _task("t1")
        approvals.require(task, "x")
        approvals.resolve(task, True, "human")
        assert events == ["required", "resolved"]


class TestDecisionEngine:
    def test_decide_priority_publishes_event(self):
        engine = DecisionEngine()
        seen: list[str] = []
        engine.events.on(OrchestratorEventType.DECISION_MADE,
                         lambda payload: seen.append(payload["priority"]))
        task = _task("t1")
        engine.decide_priority(task, 0.9)
        assert task.priority == Priority.CRITICAL
        assert seen == ["critical"]

    def test_assess_risk_counts_risky(self):
        engine = DecisionEngine()
        task = _task("t1", risk_level=RiskLevel.HIGH)
        report = engine.assess_risk(task, permissions=["*"])
        assert report["level"] == RiskLevel.CRITICAL
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("ao.risky_tasks") == 1

    def test_approval_flow_via_facade(self):
        engine = DecisionEngine()
        task = _task("t1")
        engine.require_approval(task, "gated")
        assert len(engine.pending_approvals()) == 1
        assert engine.resolve_approval(task, True, "human") is True
        assert engine.pending_approvals() == []
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("ao.approvals_required") == 1
        assert counters.get("ao.approvals_resolved") == 1

    def test_evaluate_rules(self):
        engine = DecisionEngine()
        engine.rules.add_rule("rush", lambda ctx: bool(ctx.get("urgent")),
                              lambda ctx: "go")
        fired = engine.evaluate({"urgent": True})
        assert len(fired) == 1
        assert engine.metrics.snapshot()["counters"].get(
            "ao.rules_fired") == 1

    def test_stats(self):
        engine = DecisionEngine()
        engine.rules.add_rule("a", lambda ctx: True, lambda ctx: 1)
        stats = engine.stats()
        assert stats["rules"] == 1
        assert "metrics" in stats
