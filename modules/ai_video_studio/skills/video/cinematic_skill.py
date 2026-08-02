"""Cinematic skill — AI shot-list planning plus subtitles for a brief.

Uses ``AIStudioService.generate_project`` (director → screenwriter →
storyboard) with a deterministic offline fallback, and attaches an SRT
subtitle file generated from the planned scenes.
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.core.exceptions import AIError
from modules.ai_video_studio.services.ai_studio import AIStudioService
from modules.ai_video_studio.services.subtitle_studio import SubtitleStudioService


class CinematicSkill:
    """Plan a cinematic shot list (scenes + script + subtitles) from a brief."""

    skill_id = "cinematic"
    skill_name = "Cinematic"
    skill_version = "1.0.0"
    skill_description = "Cinematic shot-list planning with scenes, script and subtitles."
    skill_category = "video"
    skill_tags = ["video", "planning", "storyboard", "subtitles"]
    skill_permissions = ["ai:llm"]

    def __init__(self) -> None:
        self._ai = AIStudioService()
        self._subtitles = SubtitleStudioService()

    async def __call__(
        self,
        prompt: str,
        *,
        num_scenes: int = 4,
        duration: float = 12.0,
        style: str = "cinematic",
        language: str = "en",
    ) -> dict[str, Any]:
        """Generate the plan; falls back to a deterministic planner offline."""
        try:
            plan = await self._ai.generate_project(
                prompt,
                num_scenes=num_scenes,
                duration=duration,
                style=style,
                language=language,
            )
        except AIError:
            plan = {
                "provider": None,
                "model": None,
                "ai_generated": False,
                "scenes": self._ai.fallback_plan(
                    prompt,
                    num_scenes=num_scenes,
                    duration=duration,
                    style=style,
                    language=language,
                ),
            }
        subtitles = self._subtitles.generate_srt(plan["scenes"])
        return {
            **plan,
            "platform": "cinematic",
            "aspect_ratio": "16:9",
            "subtitles": subtitles,
        }
