from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .reasoning_models import ReasoningResult


class ReasoningHistory:
    """Historical record of reasoning sessions."""

    def __init__(self):
        self._entries: list[dict[str, Any]] = []

    def record(self, result: ReasoningResult) -> None:
        self._entries.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "context_id": result.context_id,
            "decision": result.decision,
            "confidence": result.confidence,
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
