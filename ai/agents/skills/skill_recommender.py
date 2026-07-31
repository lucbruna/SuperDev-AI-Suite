"""Skill recommendation engine."""
from __future__ import annotations

from typing import Any, Dict, List


class SkillRecommender:
    """Recommends skills based on task requirements and agent capabilities."""

    def __init__(self) -> None:
        self._recommendation_history: List[Dict[str, Any]] = []

    def recommend(self, task: Dict[str, Any], manager: Any) -> List[Dict[str, Any]]:
        task_type = task.get("type", "general")
        keywords = task.get("keywords", [])
        category_map = {
            "code": ["coding", "development"],
            "test": ["testing", "qa"],
            "deploy": ["deployment", "infrastructure"],
            "document": ["documentation", "writing"],
            "analyze": ["analysis", "reasoning"],
        }
        target_categories = category_map.get(task_type, ["general"])
        all_skills = manager.list_all()
        scored: List[Dict[str, Any]] = []
        for skill in all_skills:
            score = 0.0
            if skill.get("category") in target_categories:
                score += 0.5
            name = skill.get("name", "").lower()
            for kw in keywords:
                if kw.lower() in name:
                    score += 0.3
            scored.append({**skill, "relevance_score": round(score, 2)})
        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        top = scored[:5]
        self._recommendation_history.append({
            "task_type": task_type,
            "recommendations": len(top),
        })
        return top

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._recommendation_history[-limit:]
