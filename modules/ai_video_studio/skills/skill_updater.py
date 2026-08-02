"""Skill updater — replaces an installed skill with a newer version."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_events import fire_sync, skill_updated
from modules.ai_video_studio.skills.skill_logger import get_skill_logger
from modules.ai_video_studio.skills.skill_registry import SkillDefinition
from modules.ai_video_studio.skills.skill_repository import get_skill_repository
from modules.ai_video_studio.skills.skill_validator import assert_valid


class SkillUpdateError(RuntimeError):
    """Raised when an update fails."""


class SkillUpdater:
    def __init__(self) -> None:
        self._repository = get_skill_repository()
        self._logger = get_skill_logger()

    def update(self, definition: SkillDefinition) -> dict[str, Any]:
        assert_valid(definition)
        current = self._repository.get(definition.id)
        if current is None:
            raise SkillUpdateError(f"skill '{definition.id}' is not installed")
        if current.version == definition.version:
            raise SkillUpdateError(
                f"skill '{definition.id}' is already at v{definition.version}"
            )
        self._repository.save(definition)
        self._logger.log(
            "updater",
            f"updated {definition.id} {current.version} -> {definition.version}",
        )
        fire_sync(skill_updated(definition.id, current.version, definition.version))
        return {
            "skill_id": definition.id,
            "old_version": current.version,
            "new_version": definition.version,
            "updated": True,
        }


_updater: SkillUpdater | None = None


def get_skill_updater() -> SkillUpdater:
    global _updater
    if _updater is None:
        _updater = SkillUpdater()
    return _updater
