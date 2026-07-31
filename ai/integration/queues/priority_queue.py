"""
Priority Queue - Priority-based processing
"""

import hashlib
import heapq
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class PriorityMessage:
    priority: int
    message_id: str
    payload: Any = None
    created_at: datetime = field(default_factory=datetime.now)

    def __lt__(self, other):
        return self.priority < other.priority


class PriorityQueue:
    def __init__(self):
        self.heap: list[PriorityMessage] = []
        self.messages: dict[str, PriorityMessage] = {}
        self.processed: list[PriorityMessage] = []

    def enqueue(self, payload: Any, priority: int = 0) -> PriorityMessage:
        message_id = hashlib.sha256(f"{str(payload)}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        msg = PriorityMessage(priority=priority, message_id=message_id, payload=payload)
        heapq.heappush(self.heap, msg)
        self.messages[message_id] = msg
        return msg

    def dequeue(self) -> PriorityMessage | None:
        if self.heap:
            msg = heapq.heappop(self.heap)
            self.processed.append(msg)
            return msg
        return None

    def peek(self) -> PriorityMessage | None:
        return self.heap[0] if self.heap else None

    def size(self) -> int:
        return len(self.heap)

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def get_message(self, message_id: str) -> PriorityMessage | None:
        return self.messages.get(message_id)

    def count(self) -> int:
        return len(self.heap)
