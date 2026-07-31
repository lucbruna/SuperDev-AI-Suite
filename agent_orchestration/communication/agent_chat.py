"""Structured chat between two agents (Volume 31)."""

from __future__ import annotations

from agent_orchestration.communication.message_bus import MessageBus
from agent_orchestration.orchestrator_models import (AgentMessage, MessageType)
from agent_orchestration.orchestrator_protocols import new_id


class AgentChat:
    """A conversation thread between two agents over the message bus."""

    def __init__(self, first_id: str, second_id: str,
                 bus: MessageBus | None = None) -> None:
        self.first_id = first_id
        self.second_id = second_id
        self.chat_id = new_id("chat")
        self.bus = bus or MessageBus()

    def say(self, sender_id: str, content: str,
            payload: dict | None = None) -> AgentMessage:
        recipient = (self.second_id if sender_id == self.first_id
                     else self.first_id)
        return self.bus.send(sender_id, recipient, content,
                             MessageType.DIRECT, payload)

    def messages(self) -> list[AgentMessage]:
        return self.bus.between(self.first_id, self.second_id)

    def transcript(self) -> list[str]:
        return [f"{message.sender_id}: {message.content}"
                for message in self.messages()]

    def count(self) -> int:
        return len(self.messages())
