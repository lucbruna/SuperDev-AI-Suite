"""Skill registry — SkillDefinition model and the name-keyed skill registry."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class SkillDefinition:
    """Immutable-ish metadata + entrypoint for a skill."""

    id: str
    name: str
    version: str
    description: str = ""
    category: str = "general"
    entrypoint: Callable[..., Any] | None = None
    permissions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SkillRegistry:
    """Name-keyed store of skill definitions."""

    def __init__(self) -> None:
        self._skills: dict[str, SkillDefinition] = {}

    def register(self, definition: SkillDefinition) -> None:
        self._skills[definition.id] = definition

    def unregister(self, skill_id: str) -> bool:
        return self._skills.pop(skill_id, None) is not None

    def get(self, skill_id: str) -> SkillDefinition | None:
        return self._skills.get(skill_id)

    def has(self, skill_id: str) -> bool:
        return skill_id in self._skills

    def list(self, category: str | None = None) -> list[dict[str, Any]]:
        items = self._skills.values()
        if category:
            items = (s for s in items if s.category == category)
        return [self.to_dict(s) for s in sorted(items, key=lambda s: s.id)]

    def categories(self) -> list[str]:
        return sorted({s.category for s in self._skills.values()})

    def count(self) -> int:
        return len(self._skills)

    @staticmethod
    def to_dict(s: SkillDefinition) -> dict[str, Any]:
        return {
            "id": s.id,
            "name": s.name,
            "version": s.version,
            "description": s.description,
            "category": s.category,
            "permissions": s.permissions,
            "tags": s.tags,
            "metadata": s.metadata,
            "has_entrypoint": s.entrypoint is not None,
        }


_registry: SkillRegistry | None = None


def get_skill_registry() -> SkillRegistry:
    """Process-wide singleton skill registry."""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry
