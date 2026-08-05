"""Hallmark skill — flagship skill backed by the hallmark engine."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.hallmark.engine import HallmarkEngine


class HallmarkSkill:
    """Run a goal through the full hallmark pipeline (plan → execute → trace)."""

    skill_id = "hallmark"
    skill_name = "Hallmark"
    skill_version = "1.0.0"
    skill_description = "Flagship orchestrating skill: plan, execute, reason, and report."
    skill_category = "hallmark"
    skill_tags = ["hallmark", "orchestration", "pipeline", "general"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        self._engine = HallmarkEngine()

    async def __call__(
        self,
        goal: str,
        *,
        steps: int = 3,
        language: str = "en",
    ) -> dict[str, Any]:
        """Execute the pipeline for ``goal`` and return the structured report."""
        result = self._engine.run(goal, steps=steps)
        result["language"] = language
        return result
