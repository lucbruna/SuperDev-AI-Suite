"""Direct messages between members."""

from __future__ import annotations

import time
from typing import Any

from collaboration.collaboration_protocols import new_id

DM_MARKER = "@dm:"


class DirectMessage:
    """A private message between two members."""

    def __init__(self, sender_id: str, recipient_id: str,
                 body: str) -> None:
        self.message_id = new_id("dm")
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.body = body
        self.created_at = time.time()
        self.read = False

    def mark_read(self) -> None:
        self.read = True

    def to_dict(self) -> dict[str, Any]:
        return {"message_id": self.message_id,
                "sender_id": self.sender_id,
                "recipient_id": self.recipient_id,
                "body": self.body, "read": self.read,
                "created_at": self.created_at}


class DirectMessageManager:
    """Private messaging between humans and AI agents."""

    def __init__(self) -> None:
        self._messages: dict[str, list[DirectMessage]] = {}

    def _key(self, a: str, b: str) -> str:
        return DM_MARKER + "|".join(sorted((a, b)))

    def send(self, sender_id: str, recipient_id: str,
             body: str) -> DirectMessage:
        message = DirectMessage(sender_id, recipient_id, body)
        self._messages.setdefault(self._key(sender_id, recipient_id),
                                  []).append(message)
        return message

    def thread(self, member_a: str, member_b: str) -> list[DirectMessage]:
        return list(self._messages.get(self._key(member_a, member_b), []))

    def unread_for(self, member_id: str) -> list[DirectMessage]:
        unread = []
        for messages in self._messages.values():
            unread.extend(m for m in messages
                          if m.recipient_id == member_id and not m.read)
        return unread

    def mark_thread_read(self, member_a: str, member_b: str) -> None:
        for message in self.thread(member_a, member_b):
            message.mark_read()

    def count(self) -> int:
        return sum(len(v) for v in self._messages.values())
