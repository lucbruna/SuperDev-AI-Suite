"""Director engine — coordinates creative direction of a production."""
from __future__ import annotations

from typing import Any


class DirectorEngine:
    """High-level direction pipeline: brief -> production plan."""

    def __init__(self) -> None:
        from modules.ai_video_studio.ai_director.production_plan import get_production_plan
        from modules.ai_video_studio.ai_director.scheduling import get_scheduling
        from modules.ai_video_studio.ai_director.team_management import get_team_management
        from modules.ai_video_studio.ai_director.budget_manager import get_budget_manager
        from modules.ai_video_studio.ai_director.shooting_plan import get_shooting_plan

        self.production_plan = get_production_plan()
        self.scheduling = get_scheduling()
        self.team = get_team_management()
        self.budget = get_budget_manager()
        self.shooting = get_shooting_plan()

    def direct(self, brief: str, duration: float = 60.0, crew: int = 3) -> dict[str, Any]:
        """Produce a full directorial plan from a brief."""
        plan = self.production_plan.build(brief, duration=duration)
        schedule = self.scheduling.build(plan)
        team = self.team.assign(plan, crew=crew)
        budget = self.budget.estimate(plan, crew=crew)
        shots = self.shooting.build(plan)
        return {
            "plan": plan,
            "schedule": schedule,
            "team": team,
            "budget": budget,
            "shots": shots,
            "brief": brief,
        }


_director_engine: DirectorEngine | None = None


def get_director_engine() -> DirectorEngine:
    global _director_engine
    if _director_engine is None:
        _director_engine = DirectorEngine()
    return _director_engine
