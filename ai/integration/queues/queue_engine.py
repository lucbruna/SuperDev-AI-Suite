"""
Queue Engine - Core queue management
"""

import collections
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class QueueState(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DRAINING = "draining"


@dataclass
class QueueMessage:
    message_id: str
    queue_name: str
    payload: Any = None
    priority: int = 0
    state: str = "pending"
    attempts: int = 0
    max_retries: int = 3
    created_at: datetime = field(default_factory=datetime.now)
    processed_at: datetime | None = None
    error: str = ""


class QueueEngine:
    def __init__(self):
        self.queues: dict[str, collections.deque] = {}
        self.queue_states: dict[str, QueueState] = {}
        self.messages: dict[str, QueueMessage] = {}
        self.processed: list[QueueMessage] = []

    def create_queue(self, name: str) -> None:
        self.queues[name] = collections.deque()
        self.queue_states[name] = QueueState.ACTIVE

    def enqueue(self, queue_name: str, payload: Any, priority: int = 0) -> QueueMessage:
        if queue_name not in self.queues:
            self.create_queue(queue_name)
        message_id = hashlib.sha256(f"{queue_name}{str(payload)}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        msg = QueueMessage(message_id=message_id, queue_name=queue_name, payload=payload, priority=priority)
        self.messages[message_id] = msg
        self.queues[queue_name].append(message_id)
        return msg

    def dequeue(self, queue_name: str) -> QueueMessage | None:
        queue = self.queues.get(queue_name)
        if not queue or not queue:
            return None
        message_id = queue.popleft()
        msg = self.messages.get(message_id)
        if msg:
            msg.state = "processing"
            msg.processed_at = datetime.now()
        return msg

    def complete(self, message_id: str) -> bool:
        msg = self.messages.get(message_id)
        if msg:
            msg.state = "completed"
            self.processed.append(msg)
            return True
        return False

    def fail(self, message_id: str, error: str = "") -> bool:
        msg = self.messages.get(message_id)
        if msg:
            msg.attempts += 1
            msg.error = error
            if msg.attempts >= msg.max_retries:
                msg.state = "dead_letter"
            else:
                msg.state = "pending"
                self.queues[msg.queue_name].append(message_id)
            return True
        return False

    def size(self, queue_name: str) -> int:
        return len(self.queues.get(queue_name, []))

    def get_queue(self, queue_name: str) -> list[QueueMessage]:
        queue = self.queues.get(queue_name, [])
        return [self.messages[mid] for mid in queue if mid in self.messages]

    def pause(self, queue_name: str) -> bool:
        if queue_name in self.queue_states:
            self.queue_states[queue_name] = QueueState.PAUSED
            return True
        return False

    def resume(self, queue_name: str) -> bool:
        if queue_name in self.queue_states:
            self.queue_states[queue_name] = QueueState.ACTIVE
            return True
        return False

    def list_queues(self) -> list[str]:
        return list(self.queues.keys())

    def count(self) -> int:
        return len(self.messages)
