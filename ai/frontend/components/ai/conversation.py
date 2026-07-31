"""
Conversation Manager
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Conversation:
    id: str
    title: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class ConversationManager:
    def __init__(self):
        self.conversations: list[Conversation] = []
        self.active_id: str | None = None

    def create(self, title: str = "New Conversation") -> Conversation:
        import uuid

        conv = Conversation(id=str(uuid.uuid4()), title=title)
        self.conversations.append(conv)
        return conv

    def get(self, conv_id: str) -> Conversation | None:
        return next((c for c in self.conversations if c.id == conv_id), None)

    def delete(self, conv_id: str) -> bool:
        for i, c in enumerate(self.conversations):
            if c.id == conv_id:
                self.conversations.pop(i)
                return True
        return False

    def list_all(self) -> list[Conversation]:
        return sorted(self.conversations, key=lambda c: c.updated_at, reverse=True)

    def render(self) -> dict[str, Any]:
        return {
            "conversations": [{"id": c.id, "title": c.title, "messageCount": c.message_count} for c in self.list_all()],
            "activeId": self.active_id,
        }
