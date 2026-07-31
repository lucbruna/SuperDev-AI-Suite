"""Subscription cancellation."""
from __future__ import annotations

import time
from typing import Any


class CancellationManager:
    def __init__(self) -> None:
        self._cancellations: list[dict[str, Any]] = []
    def cancel(self, subscription_id: str, reason: str = "", feedback: str = "") -> dict[str, Any]:
        entry = {"subscription_id": subscription_id, "reason": reason, "feedback": feedback, "cancelled_at": time.time()}
        self._cancellations.append(entry)
        return entry
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._cancellations)
    def get_by_subscription(self, subscription_id: str) -> dict[str, Any]:
        for c in self._cancellations:
            if c["subscription_id"] == subscription_id:
                return c
        return {}
    def count(self) -> int:
        return len(self._cancellations)
    def get_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._cancellations[-limit:]
    def get_by_reason(self, reason: str) -> list[dict[str, Any]]:
        return [c for c in self._cancellations if c["reason"] == reason]
