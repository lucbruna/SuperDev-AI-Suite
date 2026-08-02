"""Skill manager — lifecycle facade over installer/updater/uninstaller/engine."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_engine import SkillResult, get_skill_engine
from modules.ai_video_studio.skills.skill_installer import SkillInstaller, get_skill_installer
from modules.ai_video_studio.skills.skill_loader import load
from modules.ai_video_studio.skills.skill_registry import SkillDefinition
from modules.ai_video_studio.skills.skill_uninstaller import (
    SkillUninstaller,
    get_skill_uninstaller,
)
from modules.ai_video_studio.skills.skill_updater import SkillUpdater, get_skill_updater


class SkillManager:
    """Single entry point for the whole skill lifecycle."""

    def __init__(self) -> None:
        self._engine = get_skill_engine()
        self._installer: SkillInstaller = get_skill_installer()
        self._updater: SkillUpdater = get_skill_updater()
        self._uninstaller: SkillUninstaller = get_skill_uninstaller()

    def install(self, source: Any) -> dict[str, Any]:
        definition = load(source)
        result = self._installer.install(definition)
        self._engine.register(definition)
        result["registered"] = True
        return result

    def update(self, source: Any) -> dict[str, Any]:
        definition = load(source)
        result = self._updater.update(definition)
        self._engine.register(definition)
        result["registered"] = True
        return result

    def uninstall(self, skill_id: str) -> dict[str, Any]:
        # The uninstaller removes the skill from the shared registry via the
        # repository; unregistering here first would defeat its presence check.
        return self._uninstaller.uninstall(skill_id)

    def get(self, skill_id: str) -> SkillDefinition | None:
        return self._engine.get(skill_id)

    def has(self, skill_id: str) -> bool:
        return self._engine.has(skill_id)

    def list(self, category: str | None = None) -> list[dict[str, Any]]:
        return self._engine.list(category)

    def categories(self) -> list[str]:
        return self._engine.categories()

    async def run(
        self,
        skill_id: str,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> SkillResult:
        return await self._engine.run(skill_id, context, **kwargs)

    def snapshot(self) -> dict[str, Any]:
        return self._engine.snapshot()


_manager: SkillManager | None = None


def get_skill_manager() -> SkillManager:
    global _manager
    if _manager is None:
        _manager = SkillManager()
    return _manager
