"""Webhook delivery history."""

from __future__ import annotations

import time
from typing import Any


class WebhookHistory:
    """Tracks delivered webhook events with status."""

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def record(self, event_id: str, status: str,
               attempts: int, error: str | None = None) -> None:
        self._events.append({
            "event_id": event_id,
            "status": status,
            "attempts": attempts,
            "error": error,
            "timestamp": time.time(),
        })

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._events[-limit:])

    def count(self, status: str | None = None) -> int:
        if status is None:
            return len(self._events)
        return sum(1 for e in self._events if e["status"] == status)

    def clear(self) -> None:
        self._events.clear()
