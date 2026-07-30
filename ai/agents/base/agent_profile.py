from __future__ import annotations

from typing import Any, Dict, List


class AgentProfile:
    """Profile describing an agent's characteristics."""

    def __init__(self, agent_id: str, specialty: str = "") -> None:
        self._agent_id = agent_id
        self._specialty = specialty
        self._skills: List[str] = []

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def specialty(self) -> str:
        return self._specialty

    def add_skill(self, skill: str) -> None:
        self._skills.append(skill)

    def get_skills(self) -> List[str]:
        return list(self._skills)

    def has_skill(self, skill: str) -> bool:
        return skill in self._skills

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self._agent_id,
            "specialty": self._specialty,
            "skills": self._skills,
        }
