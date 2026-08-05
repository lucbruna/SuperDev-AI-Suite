"""Character planner — define characters/presenters for a production."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError

CHARACTER_ROLES = ("presenter", "narrator", "expert", "customer", "actor", "teacher")


class CharacterPlanner:
    """Deterministic character/role assignment per scene."""

    def plan(self, scenes: list[dict[str, Any]], *, presenter_name: str = "Presenter") -> list[dict[str, Any]]:
        if not scenes:
            raise ValidationError("scenes cannot be empty", field="scenes")
        planned: list[dict[str, Any]] = []
        for i, scene in enumerate(scenes):
            role = CHARACTER_ROLES[i % len(CHARACTER_ROLES)]
            planned.append(
                {
                    "scene_index": scene.get("index", i),
                    "character": presenter_name,
                    "role": role,
                    "on_screen": role not in ("narrator",),
                    "speaks": True,
                    "notes": f"{role.capitalize()} for scene {i + 1}",
                }
            )
        return planned

    def list_roles(self) -> list[str]:
        return list(CHARACTER_ROLES)


_character_planner: CharacterPlanner | None = None


def get_character_planner() -> CharacterPlanner:
    global _character_planner
    if _character_planner is None:
        _character_planner = CharacterPlanner()
    return _character_planner
