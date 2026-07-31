"""Skill engine for agent capability management."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from .skill_manager import SkillManager
from .skill_composer import SkillComposer
from .skill_recommender import SkillRecommender


class SkillEngine:
    """Central engine for managing, composing, and recommending agent skills."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._manager = SkillManager()
        self._composer = SkillComposer()
        self._recommender = SkillRecommender()
        self._skill_count: int = 0

    def register_skill(self, skill: Dict[str, Any]) -> Dict[str, Any]:
        self._skill_count += 1
        return self._manager.register(skill)

    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        return self._manager.get(skill_id)

    def compose_skills(self, skill_ids: List[str], task: Dict[str, Any]) -> Dict[str, Any]:
        return self._composer.compose(skill_ids, task, self._manager)

    def recommend(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._recommender.recommend(task, self._manager)

    def list_skills(self) -> List[Dict[str, Any]]:
        return self._manager.list_all()

    def get_metrics(self) -> Dict[str, Any]:
        return {"total_skills": self._skill_count, "registered": self._manager.count()}
