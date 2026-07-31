"""Webhook retry policy."""

from __future__ import annotations

import time
from typing import Any


class RetryPolicy:
    """Configures and computes retry schedules for failed deliveries."""

    def __init__(self, max_attempts: int = 3,
                 backoff: float = 1.0, factor: float = 2.0) -> None:
        self.max_attempts = max_attempts
        self.backoff = backoff
        self.factor = factor

    def should_retry(self, attempt: int) -> bool:
        """Whether attempt `attempt` (1-based) is within budget."""
        return attempt <= self.max_attempts

    def next_delay(self, attempt: int) -> float:
        """Delay in seconds before the given attempt (1-based)."""
        return self.backoff * (self.factor ** (attempt - 1))

    def deadline(self, start: float, attempt: int) -> float:
        return start + self.next_delay(attempt)

    def describe(self) -> dict[str, Any]:
        return {
            "max_attempts": self.max_attempts,
            "backoff": self.backoff,
            "factor": self.factor,
        }


class RetryManager:
    """Tracks retry state per webhook event."""

    def __init__(self, policy: RetryPolicy | None = None) -> None:
        self.policy = policy or RetryPolicy()
        self._attempts: dict[str, int] = {}
        self._next: dict[str, float] = {}

    def register(self, event_id: str) -> int:
        attempt = self._attempts.get(event_id, 0) + 1
        self._attempts[event_id] = attempt
        self._next[event_id] = time.time() + self.policy.next_delay(attempt)
        return attempt

    def attempts(self, event_id: str) -> int:
        return self._attempts.get(event_id, 0)

    def should_retry(self, event_id: str) -> bool:
        """Whether another retry is allowed after current attempts."""
        return self.policy.should_retry(self.attempts(event_id) + 1)

    def is_due(self, event_id: str) -> bool:
        return time.time() >= self._next.get(event_id, 0)

    def clear(self, event_id: str) -> None:
        self._attempts.pop(event_id, None)
        self._next.pop(event_id, None)
