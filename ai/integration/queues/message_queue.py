"""
Message Queue - Message processing
"""
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class Message:
    message_id: str
    topic: str
    body: Any = None
    attributes: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"


class MessageQueue:
    def __init__(self):
        self.messages: Dict[str, Message] = {}
        self.topics: Dict[str, List[str]] = {}
        self.subscribers: Dict[str, List[Callable]] = {}

    def publish(self, topic: str, body: Any, attributes: Dict[str, str] = None) -> Message:
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
            try:
                callback(message)
            except Exception:
                pass

    def get_message(self, message_id: str) -> Optional[Message]:
        return self.messages.get(message_id)

    def get_topic_messages(self, topic: str) -> List[Message]:
        ids = self.topics.get(topic, [])
        return [self.messages[mid] for mid in ids if mid in self.messages]

    def ack(self, message_id: str) -> bool:
        msg = self.messages.get(message_id)
        if msg:
            msg.status = "acknowledged"
            return True
        return False

    def list_topics(self) -> List[str]:
        return list(self.topics.keys())

    def count(self) -> int:
        return len(self.messages)
