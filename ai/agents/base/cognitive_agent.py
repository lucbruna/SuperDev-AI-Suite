from __future__ import annotations

from typing import Any

from .base_agent import BaseAgent


class CognitiveAgent(BaseAgent):
    """Agent with cognitive capabilities."""

    def __init__(self, agent_id: str, name: str = "") -> None:
        super().__init__(agent_id, name)
        self._knowledge: dict[str, Any] = {}

    def learn(self, key: str, value: Any) -> None:
        self._knowledge[key] = value

    def recall(self, key: str) -> Any:
        return self._knowledge.get(key)

    def reason(self, inputs: dict[str, Any]) -> str:
        if "problem" in inputs:
            return "analyzing"
        return "observing"

    def to_dict(self) -> dict[str, Any]:
        d = super().to_dict()
        d["knowledge_size"] = len(self._knowledge)
        return d
