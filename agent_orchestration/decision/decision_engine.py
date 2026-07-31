"""Decision subsystem facade (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.decision.approval_manager import ApprovalManager
from agent_orchestration.decision.priority_manager import PriorityManager
from agent_orchestration.decision.risk_analysis import RiskAnalyzer
from agent_orchestration.decision.rule_engine import RuleEngine
from agent_orchestration.orchestrator_events import (OrchestratorEvents,
                                                     OrchestratorEventType)
from agent_orchestration.orchestrator_metrics import OrchestratorMetrics
from agent_orchestration.orchestrator_models import (AgentTask, Priority,
                                                     RiskLevel)


class DecisionEngine:
    """Facade over rules, priority, risk analysis and approvals."""

    def __init__(self, rules: RuleEngine | None = None,
                 priorities: PriorityManager | None = None,
                 risks: RiskAnalyzer | None = None,
                 approvals: ApprovalManager | None = None,
                 events: OrchestratorEvents | None = None,
                 metrics: OrchestratorMetrics | None = None) -> None:
        self.rules = rules or RuleEngine()
        self.priorities = priorities or PriorityManager()
        self.risks = risks or RiskAnalyzer()
        self.approvals = approvals or ApprovalManager(events)
        self.events = events or OrchestratorEvents()
        self.metrics = metrics or OrchestratorMetrics()

    def evaluate(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        fired = self.rules.evaluate(context)
        if fired:
            self.metrics.increment("ao.rules_fired")
        return fired

    def decide_priority(self, task: AgentTask, score: float) -> Priority:
        priority = self.priorities.decide(task, score)
        self.metrics.increment("ao.priorities")
        self.events.publish(OrchestratorEventType.DECISION_MADE,
                            {"task_id": task.task_id, "kind": "priority",
                             "priority": priority.value})
        return priority

    def assess_risk(self, task: AgentTask,
                    permissions: list[str] | None = None) -> dict[str, Any]:
        report = self.risks.assess(task, permissions)
        self.metrics.increment("ao.risk_assessments")
        if report["level"] in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            self.metrics.increment("ao.risky_tasks")
        return report

    def require_approval(self, task: AgentTask, reason: str = "") -> None:
        self.approvals.require(task, reason)
        self.metrics.increment("ao.approvals_required")

    def resolve_approval(self, task: AgentTask, approved: bool,
                         approver: str = "") -> bool:
        resolved = self.approvals.resolve(task, approved, approver)
        if resolved:
            self.metrics.increment("ao.approvals_resolved")
        return resolved

    def pending_approvals(self) -> list[dict[str, Any]]:
        return self.approvals.pending()

    def stats(self) -> dict[str, Any]:
        counters = self.metrics.snapshot()["counters"]
        return {"rules": self.rules.count(),
                "pending_approvals": len(self.approvals.pending()),
                "metrics": counters}
