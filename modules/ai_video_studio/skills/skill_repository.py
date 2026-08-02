"""Skill repository — in-memory store of installed skills."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_registry import SkillDefinition, SkillRegistry


class SkillRepository:
    """Storage layer for installed skill definitions."""

    def __init__(self, registry: SkillRegistry | None = None) -> None:
        from modules.ai_video_studio.skills.skill_registry import get_skill_registry

        self._registry = registry or get_skill_registry()

    def save(self, definition: SkillDefinition) -> None:
        self._registry.register(definition)

    def remove(self, skill_id: str) -> bool:
        return self._registry.unregister(skill_id)

    def get(self, skill_id: str) -> SkillDefinition | None:
        return self._registry.get(skill_id)

    def has(self, skill_id: str) -> bool:
        return self._registry.has(skill_id)

    def list(self, category: str | None = None) -> list[dict[str, Any]]:
        return self._registry.list(category)

    def count(self) -> int:
        return self._registry.count()


_repository: SkillRepository | None = None


def get_skill_repository() -> SkillRepository:
    global _repository
    if _repository is None:
        _repository = SkillRepository()
    return _repository
