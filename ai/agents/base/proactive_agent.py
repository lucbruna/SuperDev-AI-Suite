from __future__ import annotations

from typing import Any, Dict, List

from .base_agent import BaseAgent


class ProactiveAgent(BaseAgent):
    """Agent that takes initiative."""

    def __init__(self, agent_id: str, name: str = "") -> None:
        super().__init__(agent_id, name)
        self._goals: List[str] = []

    def add_goal(self, goal: str) -> None:
        self._goals.append(goal)

    def get_goals(self) -> List[str]:
        return list(self._goals)

    def propose_actions(self) -> List[str]:
        if not self._goals:
            return []
        return [f"work_on_{g}" for g in self._goals]

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        result = super().execute(task)
        result["goals"] = self._goals
        return result
