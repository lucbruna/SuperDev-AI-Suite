from __future__ import annotations
import uuid
import time
from typing import Any, Optional
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str = "user"
    content: str = ""
    timestamp: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    id: str = ""
    session_id: str = ""
    title: str = ""
    messages: list[Message] = field(default_factory=list)
    created_at: float = 0.0
    updated_at: float = 0.0


class ConversationManager:
    def __init__(self):
        self._conversations: dict[str, Conversation] = {}

    def create(self, session_id: str, title: str = "", metadata: Optional[dict] = None) -> Conversation:
        now = time.time()
        conv = Conversation(
            id=str(uuid.uuid4()),
            session_id=session_id,
            title=title or "New Conversation",
            created_at=now,
            updated_at=now,
        )
        self._conversations[conv.id] = conv
        return conv

    def get(self, conversation_id: str) -> Optional[Conversation]:
        return self._conversations.get(conversation_id)

    def add_message(self, conversation_id: str, role: str, content: str, metadata: Optional[dict] = None) -> Optional[Message]:
        conv = self._conversations.get(conversation_id)
        if not conv:
            return None
        msg = Message(role=role, content=content, timestamp=time.time(), metadata=metadata or {})
        conv.messages.append(msg)
        conv.updated_at = time.time()
        return msg

    def get_messages(self, conversation_id: str) -> list[Message]:
        conv = self._conversations.get(conversation_id)
        return conv.messages if conv else []

    def delete(self, conversation_id: str) -> bool:
        return self._conversations.pop(conversation_id, None) is not None

    def list_by_session(self, session_id: str) -> list[Conversation]:
        return [c for c in self._conversations.values() if c.session_id == session_id]

    def update_title(self, conversation_id: str, title: str) -> bool:
        conv = self._conversations.get(conversation_id)
        if not conv:
            return False
        conv.title = title
        conv.updated_at = time.time()
        return True
