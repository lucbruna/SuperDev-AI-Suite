"""TikTok skill — vertical short-form plan with hook and call-to-action.

Short vertical (9:16) scene plan with a deterministic hook/CTA derived from
the prompt, layered on the shared AI project planner.
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.core.exceptions import AIError
from modules.ai_video_studio.services.ai_studio import AIStudioService


def _hook(prompt: str) -> str:
    words = prompt.strip().split()
    return " ".join(words[:6]) + ("…" if len(words) > 6 else "")


class TikTokSkill:
    """Plan a short vertical (9:16) video with hook and call-to-action."""

    skill_id = "tiktok"
    skill_name = "TikTok"
    skill_version = "1.0.0"
    skill_description = "Short vertical 9:16 video plan with hook and CTA."
    skill_category = "video"
    skill_tags = ["video", "tiktok", "shortform", "vertical"]
    skill_permissions = ["ai:llm"]

    def __init__(self) -> None:
        self._ai = AIStudioService()

    async def __call__(
        self,
        prompt: str,
        *,
        num_scenes: int = 3,
        duration: float = 15.0,
        style: str = "energetic",
        language: str = "en",
        call_to_action: str = "Follow for more",
    ) -> dict[str, Any]:
        """Generate the vertical plan with hook and CTA metadata."""
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
            "platform": "tiktok",
            "aspect_ratio": "9:16",
            "hook": _hook(prompt),
            "call_to_action": call_to_action,
        }
