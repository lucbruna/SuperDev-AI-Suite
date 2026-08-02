"""Avatar skill base — shared presenter logic over the real AvatarEngine.

Concrete avatar skills differ only in metadata (role, defaults); execution
picks the best-matching virtual actor and renders a real card image offline
via Pillow.
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.services.avatar_engine import AvatarEngine


class AvatarSkillBase:
    """Select an avatar for a scene and render its presenter card."""

    skill_id = "avatar"
    skill_name = "Avatar"
    skill_version = "1.0.0"
    skill_description = "Select a virtual presenter and render an avatar card."
    skill_category = "avatar"
    skill_tags: list[str] = ["avatar", "presenter"]
    skill_permissions = ["avatar:card"]
    default_style: str | None = None
    default_gender: str | None = None

    def __init__(self) -> None:
        self._engine = AvatarEngine()

    async def __call__(
        self,
        script: str = "",
        *,
        scene_type: str = "content",
        style: str | None = None,
        gender: str | None = None,
        width: int = 640,
        height: int = 640,
    ) -> dict[str, Any]:
        """Pick an avatar, render its card and attach the script for later stages."""
        profile = self._engine.select_for_scene(
            scene_type=scene_type,
            style=style or self.default_style,
            gender=gender or self.default_gender,
        )
        card_path = await self._engine.generate_avatar_card(
            profile, width=width, height=height
        )
        return {
            "avatar_id": profile.id,
            "avatar_name": profile.name,
            "avatar_style": profile.style,
            "avatar_gender": profile.gender,
            "scene_type": scene_type,
            "card_path": card_path,
            "script": script,
        }
