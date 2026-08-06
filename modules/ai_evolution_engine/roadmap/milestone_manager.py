"""Milestone manager: assigns and tracks roadmap milestones."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.config.constants import ITEM_BACKLOG, ITEM_DONE, ITEM_PLANNED
from modules.ai_evolution_engine.roadmap.roadmap_engine import RoadmapItem


@dataclass(slots=True)
class Milestone:
    """One scheduled milestone with its items."""

    name: str
    items: list[RoadmapItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "items": [i.to_dict() for i in self.items],
        }


class MilestoneManager:
    """Groups roadmap items into milestones."""

    def group(self, items: list[RoadmapItem]) -> list[Milestone]:
        grouped: dict[str, list[RoadmapItem]] = {}
        for item in items:
            grouped.setdefault(item.milestone, []).append(item)
        return [
            Milestone(name=name, items=items)
            for name, items in sorted(grouped.items())
        ]

    def mark_done(self, item: RoadmapItem) -> None:
        item.status = ITEM_DONE
