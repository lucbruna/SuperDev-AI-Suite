"""Message management."""

from __future__ import annotations

from typing import Any

from collaboration.collaboration_models import MessageKind, MessageRecord
from collaboration.collaboration_protocols import new_id
from collaboration.comments.comment_mentions import mentions_in


class MessageManager:
    """Sends and retrieves messages inside channels."""

    def __init__(self, registry: Any = None) -> None:
        self.registry = registry

    def send(self, channel_id: str, author_id: str, body: str,
             kind: MessageKind = MessageKind.CHAT,
             mentions: list[str] | None = None) -> MessageRecord | None:
        message = MessageRecord(message_id=new_id("msg"),
                                channel_id=channel_id, author_id=author_id,
                                body=body, kind=kind,
                                mentions=list(mentions or []))
        if self.registry is not None:
            self.registry.add_message(message)
        return message

    def messages_for(self, channel_id: str) -> list[MessageRecord]:
        if self.registry is None:
            return []
        return self.registry.messages_for(channel_id)

    def from_agent(self, channel_id: str, agent_id: str,
                   body: str) -> MessageRecord | None:
        return self.send(channel_id, agent_id, body,
                         kind=MessageKind.SYSTEM)

    def mentioned(self, member_id: str) -> list[MessageRecord]:
        if self.registry is None:
            return []
        all_messages = []
        for channel_id in self.registry.list_channels():
            all_messages.extend(self.registry.messages_for(channel_id))
        return [m for m in all_messages if member_id in m.mentions]

    def count(self) -> int:
        if self.registry is None:
            return 0
        total = 0
        for channel_id in self.registry.list_channels():
            total += len(self.registry.messages_for(channel_id))
        return total
