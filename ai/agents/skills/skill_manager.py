"""Skill registration and management."""
from __future__ import annotations

from typing import Any


class SkillManager:
    """Manages the lifecycle of agent skills."""

    def __init__(self) -> None:
        self._skills: dict[str, dict[str, Any]] = {}

    def register(self, skill: dict[str, Any]) -> dict[str, Any]:
        skill_id = skill.get("id", f"skill_{len(self._skills) + 1}")
        self._skills[skill_id] = {
            "id": skill_id,
            "name": skill.get("name", "Unnamed"),
            "description": skill.get("description", ""),
            "category": skill.get("category", "general"),
            "version": skill.get("version", "1.0.0"),
            "dependencies": skill.get("dependencies", []),
            "enabled": True,
        }
        return {"status": "registered", "skill_id": skill_id}

    def get(self, skill_id: str) -> dict[str, Any] | None:
        return dict(self._skills.get(skill_id)) if skill_id in self._skills else None

    def enable(self, skill_id: str) -> bool:
        if skill_id in self._skills:
            self._skills[skill_id]["enabled"] = True
            return True
        return False

    def disable(self, skill_id: str) -> bool:
        if skill_id in self._skills:
            self._skills[skill_id]["enabled"] = False
            return True
        return False

    def list_all(self) -> list[dict[str, Any]]:
        return [{"id": s["id"], "name": s["name"], "category": s["category"]} for s in self._skills.values()]

    def list_by_category(self, category: str) -> list[dict[str, Any]]:
        return [
            {"id": s["id"], "name": s["name"]}
            for s in self._skills.values()
            if s["category"] == category
        ]

    def count(self) -> int:
        return len(self._skills)
