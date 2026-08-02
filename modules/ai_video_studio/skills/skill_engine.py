"""Skill engine — orchestrates registration, security, permissions and execution."""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_events import skill_executed
from modules.ai_video_studio.skills.skill_permissions import get_skill_permissions
from modules.ai_video_studio.skills.skill_registry import (
    SkillDefinition,
    get_skill_registry,
)
from modules.ai_video_studio.skills.skill_runtime import SkillResult, get_skill_runtime
from modules.ai_video_studio.skills.skill_security import get_skill_security
from modules.ai_video_studio.skills.skill_statistics import get_skill_statistics
from modules.ai_video_studio.skills.skill_validator import assert_valid


class SkillNotFoundError(LookupError):
    def __init__(self, skill_id: str) -> None:
        self.skill_id = skill_id
        super().__init__(f"skill '{skill_id}' is not registered")


class SkillEngine:
    """High-level skill API: register, run, inspect."""

    def __init__(self) -> None:
        from modules.ai_video_studio.skills.skill_repository import get_skill_repository

        self._registry = get_skill_registry()
        self._repository = get_skill_repository()
        self._runtime = get_skill_runtime()
        self._permissions = get_skill_permissions()
        self._security = get_skill_security()
        self._statistics = get_skill_statistics()

    def register(self, definition: SkillDefinition) -> dict[str, Any]:
        """Validate and register a skill, granting its declared permissions."""
        assert_valid(definition)
        self._registry.register(definition)
        self._permissions.grant(definition.id, *definition.permissions)
        return {"skill_id": definition.id, "registered": True}

    def get(self, skill_id: str) -> SkillDefinition | None:
        return self._registry.get(skill_id)

    def has(self, skill_id: str) -> bool:
        return self._registry.has(skill_id)

    def list(self, category: str | None = None) -> list[dict[str, Any]]:
        return self._registry.list(category)

    def categories(self) -> list[str]:
        return self._registry.categories()

    async def run(
        self,
        skill_id: str,
        context: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> SkillResult:
        definition = self._registry.get(skill_id)
        if definition is None:
            raise SkillNotFoundError(skill_id)
        # Security gate first, then permissions, then execute.
        self._security.check(skill_id, definition.entrypoint)
        self._permissions.require_all(skill_id, definition.permissions)
        result = await self._runtime.execute(definition, context, **kwargs)
        self._statistics.record(
            skill_id, ok=result.ok, duration_ms=result.duration_ms
        )
        await skill_executed(
            skill_id, ok=result.ok, duration_ms=result.duration_ms, error=result.error
        )
        return result

    def snapshot(self) -> dict[str, Any]:
        return {
            "count": self._registry.count(),
            "categories": self.categories(),
            "skills": self.list(),
            "security": self._security.snapshot(),
            "permissions": self._permissions.snapshot(),
            "statistics": self._statistics.stats(),
        }


_engine: SkillEngine | None = None


def get_skill_engine() -> SkillEngine:
    global _engine
    if _engine is None:
        _engine = SkillEngine()
    return _engine
