"""
Message Queue - Message processing
"""
import contextlib
import hashlib
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Message:
    message_id: str
    topic: str
    body: Any = None
    attributes: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"


class MessageQueue:
    def __init__(self):
        self.messages: dict[str, Message] = {}
        self.topics: dict[str, list[str]] = {}
        self.subscribers: dict[str, list[Callable]] = {}

    def publish(self, topic: str, body: Any, attributes: dict[str, str] = None) -> Message:
        message_id = hashlib.sha256(f"{topic}{str(body)}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        msg = Message(message_id=message_id, topic=topic, body=body, attributes=attributes or {})
        self.messages[message_id] = msg
        self.topics.setdefault(topic, []).append(message_id)
        self._notify(topic, msg)
        return msg

    def subscribe(self, topic: str, callback: Callable) -> None:
        self.subscribers.setdefault(topic, []).append(callback)

    def _notify(self, topic: str, message: Message) -> None:
        for callback in self.subscribers.get(topic, []):
            with contextlib.suppress(Exception):
                callback(message)

    def get_message(self, message_id: str) -> Message | None:
        return self.messages.get(message_id)

    def get_topic_messages(self, topic: str) -> list[Message]:
        ids = self.topics.get(topic, [])
        return [self.messages[mid] for mid in ids if mid in self.messages]

    def ack(self, message_id: str) -> bool:
        msg = self.messages.get(message_id)
        if msg:
            msg.status = "acknowledged"
            return True
        return False

    def list_topics(self) -> list[str]:
        return list(self.topics.keys())

    def count(self) -> int:
        return len(self.messages)
