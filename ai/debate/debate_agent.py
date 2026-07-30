from __future__ import annotations

from typing import Any


class DebateAgent:
    """An agent participating in a debate."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self._knowledge_base: dict[str, Any] = {}

    def add_knowledge(self, key: str, value: Any) -> None:
        self._knowledge_base[key] = value

    async def argue(self, topic: str) -> dict[str, Any]:
        return {
            "agent": self.name,
            "role": self.role,
            "stance": "neutral",
            "points": [f"As {self.role}, I believe {topic} requires careful analysis."],
            "confidence": 0.7,
        }

    async def respond(self, counterargument: dict[str, Any]) -> dict[str, Any]:
        return {
            "agent": self.name,
            "rebuttal": f"Considering {counterargument.get('stance', 'the opposing view')}, I maintain my position.",
            "confidence": 0.65,
        }
