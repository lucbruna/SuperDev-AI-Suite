"""Priority engine: deterministic ranking of roadmap items."""
from __future__ import annotations

from modules.ai_evolution_engine.roadmap.roadmap_engine import RoadmapItem


class PriorityEngine:
    """Ranks items by priority within and across milestones."""

    def rank(self, items: list[RoadmapItem]) -> list[RoadmapItem]:
        ordered = sorted(items, key=lambda i: i.priority, reverse=True)
        return ordered

    def top(self, items: list[RoadmapItem], count: int = 5) -> list[RoadmapItem]:
        return self.rank(items)[:count]
