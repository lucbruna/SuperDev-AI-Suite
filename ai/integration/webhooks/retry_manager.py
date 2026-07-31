"""
Retry Manager - Webhook retry logic
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class RetryPolicy:
    max_retries: int = 3
    initial_delay_ms: int = 1000
    backoff_multiplier: float = 2.0
    max_delay_ms: int = 30000


@dataclass
class RetryEntry:
    entry_id: str
    webhook_id: str
    attempt: int = 0
    next_retry_at: Optional[datetime] = None
    status: str = "pending"
    last_error: str = ""


class RetryManager:
    def __init__(self):
        self.policies: Dict[str, RetryPolicy] = {}
        self.retries: Dict[str, RetryEntry] = {}

    def set_policy(self, webhook_id: str, max_retries: int = 3, initial_delay_ms: int = 1000, backoff_multiplier: float = 2.0) -> RetryPolicy:
        policy = RetryPolicy(max_retries=max_retries, initial_delay_ms=initial_delay_ms, backoff_multiplier=backoff_multiplier)
        self.policies[webhook_id] = policy
        return policy

    def schedule_retry(self, entry_id: str, webhook_id: str, attempt: int, last_error: str = "") -> RetryEntry:
        policy = self.policies.get(webhook_id, RetryPolicy())
        delay_ms = min(policy.initial_delay_ms * (policy.backoff_multiplier ** attempt), policy.max_delay_ms)
        entry = RetryEntry(entry_id=entry_id, webhook_id=webhook_id, attempt=attempt, next_retry_at=datetime.now() + timedelta(milliseconds=delay_ms), last_error=last_error)
        self.retries[entry_id] = entry
        return entry

    def should_retry(self, entry_id: str) -> bool:
        entry = self.retries.get(entry_id)
        if not entry:
            return False
        policy = self.policies.get(entry.webhook_id, RetryPolicy())
        if entry.attempt >= policy.max_retries:
            return False
        if entry.next_retry_at and datetime.now() < entry.next_retry_at:
            return False
        return True

    def mark_completed(self, entry_id: str) -> bool:
        entry = self.retries.get(entry_id)
        if entry:
            entry.status = "completed"
            return True
        return False

    def get_pending(self) -> List[RetryEntry]:
        return [e for e in self.retries.values() if e.status == "pending"]

    def get_policy(self, webhook_id: str) -> Optional[RetryPolicy]:
        return self.policies.get(webhook_id)

    def count(self) -> int:
        return len(self.retries)
