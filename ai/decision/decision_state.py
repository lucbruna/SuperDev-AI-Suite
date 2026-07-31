from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class DecisionState:
    """Tracks the lifecycle state of a decision."""

    def __init__(self, context_id: str = ""):
        self.context_id = context_id
        self.phase: str = "pending"
        self.selected_option: str = ""
        self.confidence: float = 0.0
        self.error: str | None = None
        self._history: list[dict[str, Any]] = []
        self._started_at: str = datetime.now(UTC).isoformat()

    def transition(self, phase: str) -> None:
        self.phase = phase
        self._history.append({
            "phase": phase,
            "timestamp": datetime.now(UTC).isoformat(),
        })

    def snapshot(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "phase": self.phase,
            "selected_option": self.selected_option,
            "confidence": self.confidence,
            "error": self.error,
            "started_at": self._started_at,
            "history": self._history,
        }
