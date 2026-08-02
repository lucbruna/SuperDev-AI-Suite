"""Skill loader — builds SkillDefinition instances from dicts or class objects."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_registry import SkillDefinition
from modules.ai_video_studio.skills.skill_validator import assert_valid

_DICT_KEYS = {"id", "name", "version"}


def from_dict(data: dict[str, Any]) -> SkillDefinition:
    """Build a validated SkillDefinition from a plain dict."""
    definition = SkillDefinition(
        id=str(data["id"]),
        name=str(data["name"]),
        version=str(data["version"]),
        description=str(data.get("description", "")),
        category=str(data.get("category", "general")),
        entrypoint=data.get("entrypoint"),
        permissions=list(data.get("permissions", [])),
        tags=list(data.get("tags", [])),
        metadata=dict(data.get("metadata", {})),
    )
    return assert_valid(definition)


def from_class(cls: type) -> SkillDefinition:
    """Build a SkillDefinition from a class carrying skill_* class attributes."""
    definition = SkillDefinition(
        id=str(getattr(cls, "skill_id", cls.__name__.lower())),
        name=str(getattr(cls, "skill_name", getattr(cls, "skill_id", cls.__name__))),
        version=str(getattr(cls, "skill_version", "1.0.0")),
        description=str(getattr(cls, "skill_description", "")),
        category=str(getattr(cls, "skill_category", "general")),
        entrypoint=cls if callable(cls) else None,
        permissions=list(getattr(cls, "skill_permissions", [])),
        tags=list(getattr(cls, "skill_tags", [])),
        metadata=dict(getattr(cls, "skill_metadata", {})),
    )
    return assert_valid(definition)


def load(source: Any) -> SkillDefinition:
    """Load a definition from a dict, a class, or an existing SkillDefinition."""
    if isinstance(source, SkillDefinition):
        return assert_valid(source)
    if isinstance(source, dict):
        return from_dict(source)
    if isinstance(source, type):
        return from_class(source)
    raise TypeError(f"cannot load skill from {type(source).__name__}")
