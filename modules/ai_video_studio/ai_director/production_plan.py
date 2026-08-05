"""Production plan — builds the master plan for a video production."""
from __future__ import annotations

from typing import Any


class ProductionPlan:
    """Builds a production plan from a creative brief."""

    def build(self, brief: str, duration: float = 60.0) -> dict[str, Any]:
        scenes = max(1, int(duration / 20))
        return {
            "title": brief.strip() or "Untitled production",
            "duration": duration,
            "scenes": scenes,
            "phases": ["pre", "production", "post"],
            "vision": "clean, modern, objective",
        }


_production_plan: ProductionPlan | None = None


def get_production_plan() -> ProductionPlan:
    global _production_plan
    if _production_plan is None:
        _production_plan = ProductionPlan()
    return _production_plan
