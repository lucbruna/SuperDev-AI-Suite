"""Release planner: distributes approved items into release windows."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.ai_evolution_engine.roadmap.roadmap_engine import RoadmapItem


@dataclass(slots=True)
class Release:
    """One release containing planned items."""

    version: str
    items: list[RoadmapItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "items": [i.to_dict() for i in self.items],
        }


class ReleasePlanner:
    """Places items into releases by milestone ordering."""

    _MILESTONE_ORDER = {"next_release": 0, "next_quarter": 1, "next_year": 2}

    def plan(self, items: list[RoadmapItem], base_version: str = "1.0.0") -> list[Release]:
        buckets: dict[int, list[RoadmapItem]] = {}
        for item in items:
            bucket = self._MILESTONE_ORDER.get(item.milestone, 1)
            buckets.setdefault(bucket, []).append(item)
        releases: list[Release] = []
        for i, bucket in enumerate(sorted(buckets)):
            releases.append(
                Release(
                    version=_bump(base_version, i),
                    items=sorted(buckets[bucket], key=lambda x: x.priority, reverse=True),
                )
            )
        return releases


def _bump(base: str, step: int) -> str:
    parts = base.split(".")
    minor = int(parts[1]) if len(parts) > 1 else 0
    return f"{parts[0]}.{minor + step}.0"
