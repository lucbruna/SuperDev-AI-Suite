"""Skill composition for complex task execution."""

from __future__ import annotations

from typing import Any


class SkillComposer:
    """Combines multiple skills into composite capabilities."""

    def __init__(self) -> None:
        self._compositions: list[dict[str, Any]] = []

    def compose(self, skill_ids: list[str], task: dict[str, Any], manager: Any) -> dict[str, Any]:
        available_skills = []
        missing: list[str] = []
        for sid in skill_ids:
            skill = manager.get(sid)
            if skill:
                available_skills.append(skill)
            else:
                missing.append(sid)
        execution_order = self._resolve_order(available_skills)
        composition = {
            "skill_ids": skill_ids,
            "available": len(available_skills),
            "missing": missing,
            "execution_order": execution_order,
            "task": task.get("type", "unknown"),
        }
        self._compositions.append(composition)
        return composition

    def _resolve_order(self, skills: list[dict[str, Any]]) -> list[str]:
        resolved: list[str] = []
        remaining = list(skills)
        while remaining:
            progress = False
            for skill in list(remaining):
                deps = skill.get("dependencies", [])
                if all(d in resolved for d in deps):
                    resolved.append(skill["id"])
                    remaining.remove(skill)
                    progress = True
            if not progress:
                for skill in remaining:
                    resolved.append(skill["id"])
                break
        return resolved

    def get_compositions(self) -> list[dict[str, Any]]:
        return list(self._compositions)
