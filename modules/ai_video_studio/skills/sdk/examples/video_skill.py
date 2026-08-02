"""Example skill — video planning via the AI Studio (offline fallback)."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.core.exceptions import AIError
from modules.ai_video_studio.services.ai_studio import AIStudioService


class VideoSkill:
    """Example video skill: plan scenes for a brief (deterministic offline)."""

    skill_id = "video_example"
    skill_name = "Video Example"
    skill_version = "1.0.0"
    skill_description = "Example video planning skill built on the AI Studio."
    skill_category = "video"
    skill_tags = ["example", "video", "planning"]
    skill_permissions = ["ai:llm"]

    def __init__(self) -> None:
        self._ai = AIStudioService()

    async def __call__(
        self,
        prompt: str,
        *,
        num_scenes: int = 3,
        duration: float = 9.0,
        style: str = "cinematic",
    ) -> dict[str, Any]:
        try:
            plan = await self._ai.generate_project(
                prompt, num_scenes=num_scenes, duration=duration, style=style
            )
        except AIError:
            plan = {
                "ai_generated": False,
                "scenes": self._ai.fallback_plan(
                    prompt, num_scenes=num_scenes, duration=duration, style=style, language="en"
                ),
            }
        return plan
