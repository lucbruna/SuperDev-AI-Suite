"""Roadmap engine: turns approved recommendations into roadmap plans."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.config.constants import (
    ITEM_BACKLOG,
    ITEM_PLANNED,
    REC_APPROVED,
)
from modules.ai_evolution_engine.roadmap.roadmap_config import RoadmapConfig
from modules.ai_evolution_engine.recommendation.recommendation import (
    Recommendation,
)


@dataclass(slots=True)
class RoadmapItem:
    """A planned evolution item derived from an approved recommendation."""

    recommendation_title: str
    kind: str
    milestone: str = "unscheduled"
    priority: float = 0.0
    status: str = ITEM_BACKLOG

    def to_dict(self) -> dict[str, object]:
        return {
            "recommendation_title": self.recommendation_title,
            "kind": self.kind,
            "milestone": self.milestone,
            "priority": self.priority,
            "status": self.status,
        }


@dataclass(slots=True)
class RoadmapPlan:
    """A schedule of roadmap items grouped by milestone."""

    items: list[RoadmapItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"items": [i.to_dict() for i in self.items]}


class RoadmapEngine:
    """Builds roadmap plans from approved recommendations."""

    def __init__(self, config: RoadmapConfig | None = None) -> None:
        self._config = config or RoadmapConfig()

    def plan(self, recommendations: list[Recommendation]) -> RoadmapPlan:
        items: list[RoadmapItem] = []
        for rec in recommendations:
            if rec.status not in (REC_APPROVED, ITEM_PLANNED):
                continue
            milestone = self._config.milestone_for_kind(rec.kind)
            items.append(
                RoadmapItem(
                    recommendation_title=rec.title,
                    kind=rec.kind,
                    milestone=milestone,
                    priority=rec.priority(
                        self._config.impact_weight,
                        self._config.effort_weight,
                        self._config.risk_weight,
                    ),
                    status=ITEM_PLANNED,
                )
            )
        items.sort(key=lambda i: i.priority, reverse=True)
        return RoadmapPlan(items=items)
