from __future__ import annotations

import time
from typing import Any, Dict, List


class MessageBus:
    """Message bus for agent communication."""

    def __init__(self) -> None:
        self._messages: List[Dict[str, Any]] = []
        self._inboxes: Dict[str, List[Dict[str, Any]]] = {}

    @property
    def message_count(self) -> int:
        return len(self._messages)

    def send(self, sender: str, recipient: str, content: Dict[str, Any]) -> str:
        msg_id = f"msg_{self.message_count + 1}"
        msg = {"id": msg_id, "sender": sender, "recipient": recipient, "content": content, "timestamp": time.time()}
        self._messages.append(msg)
        if recipient not in self._inboxes:
            self._inboxes[recipient] = []
        self._inboxes[recipient].append(msg)
        return msg_id

    def receive(self, agent_id: str) -> List[Dict[str, Any]]:
        return list(self._inboxes.get(agent_id, []))

    def broadcast(self, sender: str, content: Dict[str, Any], group: str = "") -> int:
        count = 0
        for agent_id in self._inboxes:
            self.send(sender, agent_id, content)
            count += 1
        return max(count, 1)

    def clear(self) -> None:
        self._messages.clear()
        self._inboxes.clear()
