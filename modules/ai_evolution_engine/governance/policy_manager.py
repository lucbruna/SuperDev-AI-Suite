"""Policy manager: deterministic rules on recommendation kinds."""
from __future__ import annotations

from dataclasses import dataclass

from modules.ai_evolution_engine.config.constants import (
    DECISION_APPROVED,
    DECISION_ESCALATED,
    DECISION_REJECTED,
)
from modules.ai_evolution_engine.config.governance_config import GovernanceConfig
from modules.ai_evolution_engine.core.evolution_context import EvolutionContext
from modules.ai_evolution_engine.governance.approval_workflow import ApprovalDecision
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)


@dataclass(slots=True)
class PolicyDecision:
    """Outcome of policy evaluation for one recommendation."""

    status: str
    reason: str = ""

    def to_dict(self) -> dict[str, object]:
        return {"status": self.status, "reason": self.reason}


class PolicyManager:
    """Checks recommendations against configured policies."""

    def __init__(self, config: GovernanceConfig | None = None) -> None:
        self._config = config or GovernanceConfig()

    def evaluate(
        self, item: Recommendation, ctx: EvolutionContext
    ) -> PolicyDecision:
        if item.kind not in self._config.allowed_recommendation_kinds:
            return PolicyDecision(
                DECISION_REJECTED, f"kind '{item.kind}' not allowed"
            )
        if item.severity == "critical":
            return PolicyDecision(DECISION_ESCALATED, "critical severity escalated")
        return PolicyDecision(DECISION_APPROVED, "policy satisfied")
