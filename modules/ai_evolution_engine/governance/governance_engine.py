"""Governance engine: gates recommendations through the approval flow."""
from __future__ import annotations

from modules.ai_evolution_engine.config.constants import (
    DECISION_APPROVED,
    DECISION_ESCALATED,
    DECISION_PENDING,
    DECISION_REJECTED,
    REC_APPROVED,
    REC_PENDING,
    REC_REJECTED,
)
from modules.ai_evolution_engine.config.governance_config import GovernanceConfig
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.governance.approval_workflow import (
    ApprovalDecision,
    ApprovalWorkflow,
)
from modules.ai_evolution_engine.governance.audit_manager import AuditManager
from modules.ai_evolution_engine.governance.policy_manager import PolicyManager
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)


class GovernanceEngine:
    """Orchestrates policy checks and approvals for recommendations."""

    def __init__(
        self,
        config: GovernanceConfig | None = None,
        policies: PolicyManager | None = None,
        workflow: ApprovalWorkflow | None = None,
        audits: AuditManager | None = None,
    ) -> None:
        self._config = config or GovernanceConfig()
        self._policies = policies or PolicyManager(self._config)
        self._workflow = workflow or ApprovalWorkflow(self._config)
        self._audits = audits or AuditManager(self._config)

    @property
    def workflow(self) -> ApprovalWorkflow:
        return self._workflow

    @property
    def audits(self) -> AuditManager:
        return self._audits

    @property
    def policies(self) -> PolicyManager:
        return self._policies

    def submit(self, item: Recommendation, ctx: EvolutionContext) -> ApprovalDecision:
        """Check policy and route to approval (or auto-approve)."""
        decision = self._policies.evaluate(item, ctx)
        if decision.status == DECISION_REJECTED:
            item.status = REC_REJECTED
            self._audits.record("rejected_by_policy", item, decision.reason)
            ctx.publish("evolution.governance_decided", decision.to_dict())
            return decision
        if decision.status == DECISION_ESCALATED:
            item.status = REC_PENDING
            decision = self._workflow.submit(item, ctx)
            self._audits.record("submitted_for_approval", item, "policy escalation")
            return decision
        # Policy said approved -> workflow decides auto vs manual
        decision = self._workflow.submit(item, ctx)
        if decision.status == DECISION_APPROVED:
            item.status = REC_APPROVED
        elif decision.status == DECISION_PENDING:
            item.status = REC_PENDING
        self._audits.record("governance_decision", item, decision.reason)
        ctx.publish("evolution.governance_decided", decision.to_dict())
        return decision

    def approve(self, item: Recommendation, ctx: EvolutionContext) -> ApprovalDecision:
        decision = self._workflow.approve(item, ctx)
        if decision.status == DECISION_APPROVED:
            item.status = REC_APPROVED
        self._audits.record("approved", item, decision.reason)
        return decision

    def reject(self, item: Recommendation, ctx: EvolutionContext) -> ApprovalDecision:
        decision = self._workflow.reject(item, ctx)
        if decision.status == DECISION_REJECTED:
            item.status = REC_REJECTED
        self._audits.record("rejected", item, decision.reason)
        return decision
