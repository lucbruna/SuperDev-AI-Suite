from __future__ import annotations

from typing import Any

from .message_bus import MessageBus


class CommunicationEngine:
    """Central communication orchestrator."""

    def __init__(self) -> None:
        self._bus = MessageBus()

    @property
    def bus(self) -> MessageBus:
        return self._bus

    def send(self, sender: str, recipient: str, content: dict[str, Any]) -> str:
        return self._bus.send(sender, recipient, content)

    def receive(self, agent_id: str) -> list[dict[str, Any]]:
        return self._bus.receive(agent_id)

    def broadcast(self, sender: str, content: dict[str, Any], group: str = "") -> int:
        return self._bus.broadcast(sender, content, group)

    def get_stats(self) -> dict[str, Any]:
        return {"total_messages": self._bus.message_count}
