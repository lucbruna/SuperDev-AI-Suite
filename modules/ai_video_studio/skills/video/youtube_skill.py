"""YouTube skill — long-form 16:9 video plan with platform metadata.

Adds YouTube-oriented framing (more scenes, suggested title and tags) on top
of the shared AI project planner, with deterministic offline fallbacks.
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.core.exceptions import AIError
from modules.ai_video_studio.services.ai_studio import AIStudioService


def _suggest_title(prompt: str) -> str:
    words = prompt.strip().split()
    return " ".join(words[:8]) + ("…" if len(words) > 8 else "")


def _suggest_tags(prompt: str) -> list[str]:
    tags: list[str] = []
    for word in prompt.strip().lower().split():
        clean = "".join(c for c in word if c.isalnum())
        if clean and clean not in tags:
            tags.append(clean)
        if len(tags) >= 8:
            break
    return tags or ["youtube"]


class YouTubeSkill:
    """Plan a long-form YouTube video (16:9) with title and tag suggestions."""

    skill_id = "youtube"
    skill_name = "YouTube"
    skill_version = "1.0.0"
    skill_description = "Long-form YouTube video plan with title, tags and 16:9 scenes."
    skill_category = "video"
    skill_tags = ["video", "youtube", "planning", "longform"]
    skill_permissions = ["ai:llm"]

    def __init__(self) -> None:
        self._ai = AIStudioService()

    async def __call__(
        self,
        prompt: str,
        *,
        num_scenes: int = 5,
        duration: float = 60.0,
        style: str = "documentary",
        language: str = "en",
    ) -> dict[str, Any]:
        """Generate the YouTube plan with deterministic platform metadata."""
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
        return {
            **plan,
            "platform": "youtube",
            "aspect_ratio": "16:9",
            "suggested_title": _suggest_title(prompt),
            "suggested_tags": _suggest_tags(prompt),
        }
