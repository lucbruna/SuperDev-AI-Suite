from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent


class AutonomousAgent(BaseAgent):
    """Agent capable of autonomous operation."""

    def __init__(self, agent_id: str, name: str = "") -> None:
        super().__init__(agent_id, name)
        self._autonomy_level: float = 0.5

    @property
    def autonomy_level(self) -> float:
        return self._autonomy_level

    def set_autonomy(self, level: float) -> None:
        self._autonomy_level = max(0.0, min(1.0, level))

    def decide(self, context: dict[str, Any]) -> str:
        if self._autonomy_level > 0.7:
            return "execute"
        return "request_guidance"

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["autonomy_level"] = self._autonomy_level
        return d
