"""Risk policy: maps risk levels to approval requirements."""
from __future__ import annotations

from dataclasses import dataclass

from modules.self_healing_engine.config._env import (
    env_bool,
    env_int,
    env_str,
)
from modules.self_healing_engine.config.constants import (
    RISK_CRITICAL,
    RISK_HIGH,
    RISK_LEVELS,
    RISK_LOW,
    RISK_MEDIUM,
)

_RISK_RANK: dict[str, int] = {
    risk: index for index, risk in enumerate(RISK_LEVELS)
}


@dataclass(slots=True)
class RiskPolicy:
    """Approval thresholds by risk level and impact scoring."""

    approval_required_from: str = RISK_MEDIUM
    auto_rollback_on_high_risk: bool = True
    max_risk_actions_per_day: int = 50
    max_impact_score: int = 100
    high_risk_threshold: int = 70
    critical_risk_threshold: int = 90

    @classmethod
    def from_env(cls) -> "RiskPolicy":
        return cls(
            approval_required_from=env_str(
                "APPROVAL_REQUIRED_FROM", RISK_MEDIUM
            ),
            auto_rollback_on_high_risk=env_bool(
                "AUTO_ROLLBACK_ON_HIGH_RISK", True
            ),
            max_risk_actions_per_day=env_int("MAX_RISK_ACTIONS_PER_DAY", 50),
            max_impact_score=env_int("MAX_IMPACT_SCORE", 100),
            high_risk_threshold=env_int("HIGH_RISK_THRESHOLD", 70),
            critical_risk_threshold=env_int("CRITICAL_RISK_THRESHOLD", 90),
        )

    def requires_approval(self, risk: str) -> bool:
        approval_rank = _RISK_RANK.get(
            self.approval_required_from, _RISK_RANK[RISK_MEDIUM]
        )
        return _RISK_RANK.get(risk, _RISK_RANK[RISK_MEDIUM]) >= approval_rank

    def risk_for_impact(self, impact_score: int) -> str:
        if impact_score >= self.critical_risk_threshold:
            return RISK_CRITICAL
        if impact_score >= self.high_risk_threshold:
            return RISK_HIGH
        if impact_score > 0:
            return RISK_MEDIUM
        return RISK_LOW

    def to_dict(self) -> dict[str, object]:
        return {
            "approval_required_from": self.approval_required_from,
            "auto_rollback_on_high_risk": self.auto_rollback_on_high_risk,
            "max_risk_actions_per_day": self.max_risk_actions_per_day,
            "max_impact_score": self.max_impact_score,
            "high_risk_threshold": self.high_risk_threshold,
            "critical_risk_threshold": self.critical_risk_threshold,
        }
