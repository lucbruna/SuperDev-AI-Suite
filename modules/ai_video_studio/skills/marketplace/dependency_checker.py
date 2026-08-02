"""Dependency checker — validates skill dependency declarations.

Skills declare dependencies in ``metadata["depends_on"]`` as a mapping of
``skill_id -> version`` (or a list of skill ids). The checker validates
them against a map of available skills (id → installed version).
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_registry import SkillDefinition


def _dependencies_of(definition: SkillDefinition) -> dict[str, str]:
    raw = definition.metadata.get("depends_on", {})
    if isinstance(raw, dict):
        return {str(k): str(v) for k, v in raw.items()}
    if isinstance(raw, (list, tuple)):
        return {str(item): "*" for item in raw}
    return {}


class DependencyChecker:
    """Validates ``depends_on`` declarations against available skills."""

    def __init__(self, available: dict[str, str] | None = None) -> None:
        self._available: dict[str, str] = dict(available or {})

    def register_available(self, skill_id: str, version: str) -> None:
        self._available[skill_id] = version

    def missing(self, definition: SkillDefinition) -> list[str]:
        deps = _dependencies_of(definition)
        return [sid for sid in deps if sid not in self._available]

    def check(self, definition: SkillDefinition) -> dict[str, Any]:
        deps = _dependencies_of(definition)
        errors: list[str] = []
        for sid, required in deps.items():
            installed = self._available.get(sid)
            if installed is None:
                errors.append(f"missing dependency '{sid}'")
                continue
            if required not in ("*", installed):
                errors.append(
                    f"dependency '{sid}' requires {required}, installed {installed}"
                )
        return {
            "skill_id": definition.id,
            "ok": not errors,
            "dependencies": deps,
            "errors": errors,
        }
