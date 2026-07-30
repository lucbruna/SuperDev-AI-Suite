from __future__ import annotations

from typing import Any, Dict, List, Optional

from .message_bus import MessageBus


class CommunicationEngine:
    """Central communication orchestrator."""

    def __init__(self) -> None:
        self._bus = MessageBus()

    @property
    def bus(self) -> MessageBus:
        return self._bus

    def send(self, sender: str, recipient: str, content: Dict[str, Any]) -> str:
        return self._bus.send(sender, recipient, content)

    def receive(self, agent_id: str) -> List[Dict[str, Any]]:
        return self._bus.receive(agent_id)

    def broadcast(self, sender: str, content: Dict[str, Any], group: str = "") -> int:
        return self._bus.broadcast(sender, content, group)

    def get_stats(self) -> Dict[str, Any]:
        return {"total_messages": self._bus.message_count}
