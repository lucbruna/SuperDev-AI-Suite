"""Roadmap configuration."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RoadmapConfig:
    """Deterministic roadmap planning behaviour."""

    impact_weight: float = 0.5
    effort_weight: float = 0.2
    risk_weight: float = 0.3
    milestones: tuple[str, ...] = (
        "next_release",
        "next_quarter",
        "next_year",
    )
    kind_milestones: dict[str, str] = field(
        default_factory=lambda: {
            "security": "next_release",
            "performance": "next_release",
            "dependency": "next_quarter",
            "architecture": "next_quarter",
            "modernization": "next_year",
        }
    )

    def milestone_for_kind(self, kind: str) -> str:
        return self.kind_milestones.get(kind, "next_quarter")
