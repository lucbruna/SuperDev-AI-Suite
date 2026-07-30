from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .decision_models import DecisionResult


class DecisionHistory:
    """Historical record of past decisions."""

    def __init__(self):
        self._entries: list[dict[str, Any]] = []

    def record(self, result: DecisionResult) -> None:
        self._entries.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "context_id": result.context_id,
            "decision": result.decision,
            "confidence": result.confidence,
            "alternatives": result.alternatives,
        })

    def search(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        return [e for e in self._entries if q in e["decision"].lower()]

    def recent(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._entries[-limit:]

    def clear(self) -> None:
        self._entries.clear()

    def count(self) -> int:
        return len(self._entries)
