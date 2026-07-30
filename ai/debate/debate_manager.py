from __future__ import annotations

from typing import Any


class DebateManager:
    """Manages debate flow and state."""

    def __init__(self) -> None:
        self._topic: str = ""
        self._arguments: dict[str, Any] = {}
        self._round = 0

    def set_topic(self, topic: str) -> None:
        self._topic = topic
        self._round = 0

    def record_argument(self, agent_name: str, argument: Any) -> None:
        self._round += 1
        self._arguments[agent_name] = argument

    async def get_state(self) -> dict[str, Any]:
        return {
            "topic": self._topic,
            "round": self._round,
            "participants": list(self._arguments.keys()),
        }

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        return await self.get_state()
