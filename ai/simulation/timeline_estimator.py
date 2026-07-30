from __future__ import annotations

from typing import Any


class TimelineEstimator:
    """Estimates timeline and milestones for scenarios."""

    def __init__(self) -> None:
        self._milestones: list[dict[str, Any]] = []

    def add_milestone(self, name: str, duration: float) -> None:
        self._milestones.append({"name": name, "duration": duration})

    async def estimate(self, scenario: dict[str, Any]) -> dict[str, Any]:
        steps = scenario.get("steps", [])
        total_duration = sum(step.get("estimated_duration", 10) for step in steps)
        milestones = []
        current_time = 0.0
        for step in steps:
            duration = step.get("estimated_duration", 10)
            current_time += duration
            milestones.append({
                "step": step.get("id", "unknown"),
                "duration": duration,
                "cumulative_time": current_time,
            })
        return {
            "total_duration_seconds": total_duration,
            "total_duration_readable": f"{total_duration // 60}m {total_duration % 60}s",
            "milestones": milestones,
        }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        scenario = context.get("scenario", {})
        return await self.estimate(scenario)
