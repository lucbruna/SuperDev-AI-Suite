"""Skill assignment system for agents."""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class SkillAssignment:
    """Manages skill assignments for agents."""

    def __init__(self) -> None:
        self._assignments: Dict[str, List[str]] = {}
        self._skill_registry: Dict[str, Dict[str, Any]] = {}

    def register_skill(self, skill_name: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self._skill_registry[skill_name] = metadata or {}

    def assign_skill(self, agent_id: str, skill_name: str) -> bool:
        if agent_id not in self._assignments:
            self._assignments[agent_id] = []
        if skill_name not in self._assignments[agent_id]:
            self._assignments[agent_id].append(skill_name)
            return True
        return False

    def remove_skill(self, agent_id: str, skill_name: str) -> bool:
        skills = self._assignments.get(agent_id, [])
        if skill_name in skills:
            skills.remove(skill_name)
            return True
        return False

    def get_skills(self, agent_id: str) -> List[str]:
        return list(self._assignments.get(agent_id, []))

    def get_agents_with_skill(self, skill_name: str) -> List[str]:
        return [
            aid for aid, skills in self._assignments.items()
            if skill_name in skills
        ]

    def match_skills_to_task(self, required_skills: List[str]) -> Dict[str, int]:
        scores: Dict[str, int] = {}
        for agent_id, skills in self._assignments.items():
            match_count = sum(1 for s in required_skills if s in skills)
            if match_count > 0:
                scores[agent_id] = match_count
        return dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))

    def suggest_skills(self, agent_id: str) -> List[str]:
        assigned = set(self._assignments.get(agent_id, []))
        return [
            s for s in self._skill_registry
            if s not in assigned
        ]

    def clear(self) -> None:
        self._assignments.clear()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "agents": len(self._assignments),
            "skills": len(self._skill_registry),
            "assignments": {k: list(v) for k, v in self._assignments.items()},
        }
