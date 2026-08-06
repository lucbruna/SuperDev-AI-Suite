"""Approval workflow: deterministic decision routing."""
from __future__ import annotations

from dataclasses import dataclass

from modules.ai_evolution_engine.config.constants import (
    DECISION_APPROVED,
    DECISION_PENDING,
    DECISION_REJECTED,
)
from modules.ai_evolution_engine.config.governance_config import GovernanceConfig
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)

_SEVERITY_RANK = {"info": 0, "minor": 1, "major": 2, "critical": 3}


@dataclass(slots=True)
class ApprovalDecision:
    """Result of an approval action."""

    status: str
    reason: str = ""

    def to_dict(self) -> dict[str, object]:
        return {"status": self.status, "reason": self.reason}


class ApprovalWorkflow:
    """Routes recommendations: auto-approve low severity or await operator."""

    def __init__(self, config: GovernanceConfig | None = None) -> None:
        self._config = config or GovernanceConfig()
        self._pending: dict[str, Recommendation] = {}

    def pending_items(self) -> list[Recommendation]:
        return list(self._pending.values())

    def submit(
        self, item: Recommendation, ctx: EvolutionContext
    ) -> ApprovalDecision:
        threshold = _SEVERITY_RANK.get(
            self._config.auto_approve_severity, 0
        )
        if _SEVERITY_RANK.get(item.severity, 0) <= threshold:
            return ApprovalDecision(DECISION_APPROVED, "auto-approved by severity")
        if not self._config.require_approval:
            return ApprovalDecision(DECISION_APPROVED, "approval disabled")
        self._pending[item.title] = item
        ctx.state.set_open_decisions(len(self._pending))
        return ApprovalDecision(DECISION_PENDING, "awaiting operator approval")

    def approve(
        self, item: Recommendation, ctx: EvolutionContext
    ) -> ApprovalDecision:
        self._pending.pop(item.title, None)
        ctx.state.set_open_decisions(len(self._pending))
        return ApprovalDecision(DECISION_APPROVED, "approved by operator")

    def reject(
        self, item: Recommendation, ctx: EvolutionContext
    ) -> ApprovalDecision:
        self._pending.pop(item.title, None)
        ctx.state.set_open_decisions(len(self._pending))
        return ApprovalDecision(DECISION_REJECTED, "rejected by operator")
