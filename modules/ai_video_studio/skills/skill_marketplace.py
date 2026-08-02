"""Skill marketplace — local catalog of skills available for installation."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from modules.ai_video_studio.skills.skill_registry import SkillDefinition


@dataclass
class MarketplaceEntry:
    skill_id: str
    name: str
    version: str
    description: str = ""
    category: str = "general"
    tags: list[str] = field(default_factory=list)
    # A loader callable: (entry) -> SkillDefinition
    definition: SkillDefinition | None = None


class SkillMarketplace:
    """In-memory public catalog; entries can provide ready SkillDefinitions."""

    def __init__(self) -> None:
        self._entries: dict[str, MarketplaceEntry] = {}

    def publish(self, entry: MarketplaceEntry) -> None:
        self._entries[entry.skill_id] = entry

    def publish_definition(self, definition: SkillDefinition) -> None:
        self.publish(
            MarketplaceEntry(
                skill_id=definition.id,
                name=definition.name,
                version=definition.version,
                description=definition.description,
                category=definition.category,
                tags=definition.tags,
                definition=definition,
            )
        )

    def get(self, skill_id: str) -> MarketplaceEntry | None:
        return self._entries.get(skill_id)

    def fetch(self, skill_id: str) -> SkillDefinition | None:
        entry = self._entries.get(skill_id)
        if entry is None:
            return None
        if entry.definition is not None:
            return entry.definition
        return None

    def unpublish(self, skill_id: str) -> bool:
        return self._entries.pop(skill_id, None) is not None

    def list(self, category: str | None = None) -> list[dict[str, Any]]:
        items = self._entries.values()
        if category:
            items = (e for e in items if e.category == category)
        return [
            {
                "skill_id": e.skill_id,
                "name": e.name,
                "version": e.version,
                "description": e.description,
                "category": e.category,
                "tags": e.tags,
                "installable": e.definition is not None,
            }
            for e in sorted(items, key=lambda e: e.skill_id)
        ]


_marketplace: SkillMarketplace | None = None


def get_skill_marketplace() -> SkillMarketplace:
    global _marketplace
    if _marketplace is None:
        _marketplace = SkillMarketplace()
    return _marketplace
