"""Skill installer — installs a validated skill into the repository + registry."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_events import fire_sync, skill_installed
from modules.ai_video_studio.skills.skill_logger import get_skill_logger
from modules.ai_video_studio.skills.skill_registry import SkillDefinition
from modules.ai_video_studio.skills.skill_repository import get_skill_repository
from modules.ai_video_studio.skills.skill_validator import assert_valid


class SkillInstallError(RuntimeError):
    """Raised when installation fails."""


class SkillInstaller:
    def __init__(self) -> None:
        self._repository = get_skill_repository()
        self._logger = get_skill_logger()

    def install(self, definition: SkillDefinition) -> dict[str, Any]:
        assert_valid(definition)
        existing = self._repository.get(definition.id)
        if existing and existing.version == definition.version:
            raise SkillInstallError(
                f"skill '{definition.id}' v{definition.version} is already installed"
            )
        self._repository.save(definition)
        self._logger.log(
            "installer",
            f"installed {definition.id} v{definition.version}",
            payload={"category": definition.category},
        )
        fire_sync(skill_installed(definition.id, definition.version))
        return {
            "skill_id": definition.id,
            "version": definition.version,
            "installed": True,
        }


_installer: SkillInstaller | None = None


def get_skill_installer() -> SkillInstaller:
    global _installer
    if _installer is None:
        _installer = SkillInstaller()
    return _installer
