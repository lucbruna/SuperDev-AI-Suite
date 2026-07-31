from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class ReasoningState:
    """Tracks the current state of a reasoning session."""

    def __init__(self, session_id: str = ""):
        self.session_id = session_id
        self.step: int = 0
        self.phase: str = "idle"
        self.hypothesis: str = ""
        self.confidence: float = 0.0
        self.error: str | None = None
        self._history: list[dict[str, Any]] = []
        self._started_at: str = datetime.now(UTC).isoformat()

    def transition(self, phase: str) -> None:
        self.step += 1
        self.phase = phase
        self._history.append({"step": self.step, "phase": phase, "timestamp": datetime.now(UTC).isoformat()})

    def snapshot(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "step": self.step,
            "phase": self.phase,
            "hypothesis": self.hypothesis,
            "confidence": self.confidence,
            "error": self.error,
            "started_at": self._started_at,
            "history": self._history,
        }
