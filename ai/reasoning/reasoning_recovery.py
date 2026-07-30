from __future__ import annotations

from typing import Any

from .reasoning_checkpoint import ReasoningCheckpoint
from .reasoning_snapshot import ReasoningSnapshot
from .reasoning_state import ReasoningState


class ReasoningRecovery:
    """Recovery mechanisms for reasoning failures."""

    def __init__(self):
        self._checkpoint = ReasoningCheckpoint()
        self._snapshot = ReasoningSnapshot()

    def recover_from_checkpoint(self, checkpoint_id: str) -> dict[str, Any] | None:
        return self._checkpoint.load(checkpoint_id)

    def recover_from_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        return self._snapshot.get(snapshot_id)

    def save_recovery_point(self, state: ReasoningState) -> str:
        return self._checkpoint.save(state)

    def list_recovery_points(self) -> list[str]:
        return self._checkpoint.list()

    def status(self) -> dict[str, Any]:
        return {
            "checkpoints": len(self._checkpoint.list()),
            "snapshots": len(self._snapshot.list()),
        }
