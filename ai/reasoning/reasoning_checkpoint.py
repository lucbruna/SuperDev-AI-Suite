from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .reasoning_state import ReasoningState


class ReasoningCheckpoint:
    """Checkpoint for saving and restoring reasoning state."""

    def __init__(self):
        self._checkpoints: dict[str, dict[str, Any]] = {}

    def save(self, state: ReasoningState) -> str:
        checkpoint_id = f"cp_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{state.session_id}"
        self._checkpoints[checkpoint_id] = state.snapshot()
        return checkpoint_id

    def load(self, checkpoint_id: str) -> dict[str, Any] | None:
        return self._checkpoints.get(checkpoint_id)

    def list(self) -> list[str]:
        return list(self._checkpoints.keys())

    def delete(self, checkpoint_id: str) -> bool:
        return self._checkpoints.pop(checkpoint_id, None) is not None

    def clear(self) -> None:
        self._checkpoints.clear()
