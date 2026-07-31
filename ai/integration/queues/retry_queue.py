"""
Retry Queue - Failed message retry
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import hashlib


@dataclass
class RetryMessage:
    message_id: str
    original_queue: str
    payload: Any = None
    attempt: int = 0
    max_retries: int = 3
    next_retry_at: Optional[datetime] = None
    last_error: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class RetryQueue:
    def __init__(self):
        self.messages: Dict[str, RetryMessage] = {}
        self.backoff_base: int = 5
        self.backoff_multiplier: float = 2.0

    def add(self, message_id: str, original_queue: str, payload: Any = None, attempt: int = 0, max_retries: int = 3, last_error: str = "") -> RetryMessage:
        delay_seconds = self.backoff_base * (self.backoff_multiplier ** attempt)
        msg = RetryMessage(message_id=message_id, original_queue=original_queue, payload=payload, attempt=attempt, max_retries=max_retries, next_retry_at=datetime.now() + timedelta(seconds=delay_seconds), last_error=last_error)
        self.messages[message_id] = msg
        return msg

    def get_ready(self) -> List[RetryMessage]:
        now = datetime.now()
        return [m for m in self.messages.values() if m.next_retry_at and m.next_retry_at <= now and m.attempt < m.max_retries]

    def mark_retried(self, message_id: str) -> bool:
        if message_id in self.messages:
            del self.messages[message_id]
            return True
        return False

    def mark_failed(self, message_id: str) -> bool:
        msg = self.messages.get(message_id)
        if msg:
            msg.attempt = msg.max_retries
            return True
        return False

    def get_message(self, message_id: str) -> Optional[RetryMessage]:
        return self.messages.get(message_id)

    def list_all(self) -> List[RetryMessage]:
        return list(self.messages.values())

    def count(self) -> int:
        return len(self.messages)
