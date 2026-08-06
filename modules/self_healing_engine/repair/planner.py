"""Repair planning: risk assessment and safe plan construction."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.self_healing_engine.config.repair_rules import RepairRulesConfig
from modules.self_healing_engine.config.risk_policy import RiskPolicy
from modules.self_healing_engine.config.security_policy import SecurityPolicy
from modules.self_healing_engine.config.constants import (
    RISK_LEVELS,
    RISK_LOW,
)

_RISK_RANK: dict[str, int] = {
    risk: index for index, risk in enumerate(RISK_LEVELS)
}
from modules.self_healing_engine.core.healing_context import HealingContext


class HealingRepairError(RuntimeError):
    """Raised on invalid repair plans."""


@dataclass(slots=True)
class RepairPlan:
    """A validated, risk-assessed repair to be executed."""

    kind: str
    target: str
    description: str = ""
    risk: str = RISK_LOW
    impact_score: int = 0
    requires_approval: bool = False
    steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "target": self.target,
            "description": self.description,
            "risk": self.risk,
            "impact_score": self.impact_score,
            "requires_approval": self.requires_approval,
            "steps": list(self.steps),
        }


class RepairPlanner:
    """Builds repair plans subject to repair rules, risk and security policy."""

    def __init__(
        self,
        risk_policy: RiskPolicy | None = None,
        security_policy: SecurityPolicy | None = None,
        rules: RepairRulesConfig | None = None,
    ) -> None:
        self._risk_policy = risk_policy or RiskPolicy()
        self._security_policy = security_policy or SecurityPolicy()
        self._rules = rules or RepairRulesConfig()

    def assess(self, kind: str, impact_score: int) -> tuple[str, bool]:
        risk = self._risk_policy.risk_for_impact(impact_score)
        # Repairs below the auto-approval threshold run unattended; at or
        # above it, human approval is required (repair rules policy).
        threshold = _RISK_RANK.get(
            self._rules.auto_approve_below_risk, _RISK_RANK[RISK_LOW]
        )
        requires_approval = _RISK_RANK.get(risk, 0) >= threshold
        return risk, requires_approval

    def plan(
        self,
        kind: str,
        target: str,
        ctx: HealingContext,
        impact_score: int = 0,
        description: str = "",
    ) -> RepairPlan:
        if not self._rules.allows_repair_kind(kind):
            raise HealingRepairError(f"repair kind not allowed: {kind}")
        if self._security_policy.is_path_protected(target):
            raise HealingRepairError(f"target path is protected: {target}")
        risk, requires_approval = self.assess(kind, impact_score)
        plan = RepairPlan(
            kind=kind,
            target=target,
            description=description,
            risk=risk,
            impact_score=impact_score,
            requires_approval=requires_approval,
            steps=[f"repair:{kind}:{target}"],
        )
        ctx.publish(
            "repair.planned",
            {
                "kind": kind,
                "target": target,
                "risk": risk,
                "requires_approval": requires_approval,
            },
        )
        return plan
