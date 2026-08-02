"""Skill validator — checks SkillDefinition fields and semantic versions."""
from __future__ import annotations
import re

from modules.ai_video_studio.skills.skill_registry import SkillDefinition

_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


class SkillValidationError(ValueError):
    """Raised when a skill definition is invalid."""


def validate(definition: SkillDefinition) -> list[str]:
    """Return a list of validation errors (empty when the definition is valid)."""
    errors: list[str] = []
    if not definition.id or not _ID_PATTERN.match(definition.id):
        errors.append(f"invalid id '{definition.id}' (lowercase snake_case, 2-64 chars)")
    if not definition.name or not definition.name.strip():
        errors.append("name is required")
    if not _SEMVER.match(definition.version):
        errors.append(f"invalid version '{definition.version}' (expected x.y.z)")
    if not definition.category or not definition.category.strip():
        errors.append("category is required")
    if definition.entrypoint is not None and not callable(definition.entrypoint):
        errors.append("entrypoint must be callable or None")
    return errors


def assert_valid(definition: SkillDefinition) -> SkillDefinition:
    """Raise SkillValidationError when the definition is invalid."""
    errors = validate(definition)
    if errors:
        raise SkillValidationError(f"skill '{definition.id}' invalid: {'; '.join(errors)}")
    return definition


def is_valid(definition: SkillDefinition) -> bool:
    return not validate(definition)
