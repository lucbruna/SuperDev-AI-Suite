"""Skill uninstaller — removes an installed skill from the repository + registry."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_events import fire_sync, skill_uninstalled
from modules.ai_video_studio.skills.skill_logger import get_skill_logger
from modules.ai_video_studio.skills.skill_repository import get_skill_repository


class SkillUninstallError(RuntimeError):
    """Raised when uninstallation fails."""


class SkillUninstaller:
    def __init__(self) -> None:
        self._repository = get_skill_repository()
        self._logger = get_skill_logger()

    def uninstall(self, skill_id: str) -> dict[str, Any]:
        if not self._repository.has(skill_id):
            raise SkillUninstallError(f"skill '{skill_id}' is not installed")
        removed = self._repository.remove(skill_id)
        if not removed:
            raise SkillUninstallError(f"failed to remove skill '{skill_id}'")
        self._logger.log("uninstaller", f"uninstalled {skill_id}")
        fire_sync(skill_uninstalled(skill_id))
        return {"skill_id": skill_id, "uninstalled": True}


_uninstaller: SkillUninstaller | None = None


def get_skill_uninstaller() -> SkillUninstaller:
    global _uninstaller
    if _uninstaller is None:
        _uninstaller = SkillUninstaller()
    return _uninstaller
