"""Example skill — avatar presenter card via the AvatarEngine."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.services.avatar_engine import AvatarEngine


class AvatarSkill:
    """Example avatar skill: render a presenter card for a scene."""

    skill_id = "avatar_example"
    skill_name = "Avatar Example"
    skill_version = "1.0.0"
    skill_description = "Example avatar skill built on the AvatarEngine."
    skill_category = "avatar"
    skill_tags = ["example", "avatar", "presenter"]
    skill_permissions = ["avatar:card"]

    def __init__(self) -> None:
        self._engine = AvatarEngine()

    async def __call__(
        self,
        script: str = "",
        *,
        scene_type: str = "content",
        style: str | None = None,
        gender: str | None = None,
    ) -> dict[str, Any]:
        profile = self._engine.select_for_scene(
            scene_type=scene_type, style=style, gender=gender
        )
        card_path = await self._engine.generate_avatar_card(profile)
        return {
            "avatar_id": profile.id,
            "avatar_name": profile.name,
            "card_path": card_path,
            "script": script,
        }
