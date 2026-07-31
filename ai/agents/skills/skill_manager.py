"""Skill registration and management."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class SkillManager:
    """Manages the lifecycle of agent skills."""

    def __init__(self) -> None:
        self._skills: Dict[str, Dict[str, Any]] = {}

    def register(self, skill: Dict[str, Any]) -> Dict[str, Any]:
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

    def get(self, skill_id: str) -> Optional[Dict[str, Any]]:
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

    def list_all(self) -> List[Dict[str, Any]]:
        return [{"id": s["id"], "name": s["name"], "category": s["category"]} for s in self._skills.values()]

    def list_by_category(self, category: str) -> List[Dict[str, Any]]:
        return [
            {"id": s["id"], "name": s["name"]}
            for s in self._skills.values()
            if s["category"] == category
        ]

    def count(self) -> int:
        return len(self._skills)
