"""Message bus between agents (Volume 31)."""

from __future__ import annotations

from typing import Any

from agent_orchestration.orchestrator_models import (AgentMessage, MessageType)
from agent_orchestration.orchestrator_protocols import new_id, now


class MessageBus:
    """Sends direct/broadcast messages and keeps per-recipient inboxes."""

    def __init__(self) -> None:
        self._messages: list[AgentMessage] = []
        self._inbox: dict[str, list[AgentMessage]] = {}

    def send(self, sender_id: str, recipient_id: str, content: str = "",
             message_type: MessageType = MessageType.DIRECT,
             payload: dict[str, Any] | None = None) -> AgentMessage:
        message = AgentMessage(
            message_id=new_id("message"), sender_id=sender_id,
            recipient_id=recipient_id, message_type=message_type,
            content=content, payload=dict(payload or {}), created_at=now())
        self._messages.append(message)
        if message_type == MessageType.BROADCAST:
            for inbox in self._inbox.values():
                inbox.append(message)
        else:
            self._inbox.setdefault(recipient_id, []).append(message)
        return message

    def inbox(self, agent_id: str) -> list[AgentMessage]:
        # Opening an inbox registers the agent, so broadcasts reach it.
        return self._inbox.setdefault(agent_id, [])

    def history(self) -> list[AgentMessage]:
        return list(self._messages)

    def count(self) -> int:
        return len(self._messages)

    def between(self, first_id: str, second_id: str) -> list[AgentMessage]:
        return [message for message in self._messages
                if {message.sender_id, message.recipient_id} ==
                {first_id, second_id}]
