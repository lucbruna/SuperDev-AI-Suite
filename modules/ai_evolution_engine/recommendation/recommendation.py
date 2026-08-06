"""Recommendation domain model."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.config.constants import REC_DRAFT, SEVERITY_INFO


@dataclass(slots=True)
class Recommendation:
    """A proposed evolution, never applied automatically."""

    kind: str
    title: str
    description: str = ""
    target: str = ""
    severity: str = SEVERITY_INFO
    impact_score: float = 0.0  # 0..1 expected benefit
    effort_score: float = 0.0  # 0..1 required effort
    risk_score: float = 0.0    # 0..1 implementation risk
    status: str = REC_DRAFT
    evidence: list[str] = field(default_factory=list)

    def priority(self, impact_weight: float = 0.5, effort_weight: float = 0.2, risk_weight: float = 0.3) -> float:
        """Deterministic priority: weighted benefit net of effort and risk."""
        return round(
            impact_weight * self.impact_score
            - effort_weight * self.effort_score
            - risk_weight * self.risk_score,
            4,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "title": self.title,
            "description": self.description,
            "target": self.target,
            "severity": self.severity,
            "impact_score": self.impact_score,
            "effort_score": self.effort_score,
            "risk_score": self.risk_score,
            "status": self.status,
            "evidence": list(self.evidence),
            "priority": self.priority(),
        }
