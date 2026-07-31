"""Firing history for triggers."""

from __future__ import annotations

import time
from typing import Any

from automation.triggers.trigger_models import TriggerEvent


class TriggerHistory:
    """Append-only log of trigger firings."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def record(self, trigger_id: str, event: TriggerEvent | None = None) -> None:
        self._records.append({
            "trigger_id": trigger_id,
            "event_type": event.event_type if event else None,
            "timestamp": time.time(),
        })

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._records[-limit:])

    def count(self, trigger_id: str | None = None) -> int:
        if trigger_id is None:
            return len(self._records)
        return sum(1 for r in self._records if r["trigger_id"] == trigger_id)

    def clear(self) -> None:
        self._records.clear()
