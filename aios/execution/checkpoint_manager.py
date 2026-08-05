"""CheckpointManager: versioned in-memory state snapshots."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Checkpoint:
    checkpoint_id: str
    state: dict[str, Any]
    created_at: float = field(default_factory=time.time)
    label: str = ""


class CheckpointManager:
    """Save/load/restore of state snapshots with sequential ids."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, Checkpoint] = {}
        self._seq = 0

    def save(self, state: dict[str, Any], label: str = "") -> str:
        self._seq += 1
        checkpoint_id = f"ckpt-{self._seq:04d}"
        self._checkpoints[checkpoint_id] = Checkpoint(
            checkpoint_id=checkpoint_id,
            state=dict(state),
            label=label,
        )
        return checkpoint_id

    def load(self, checkpoint_id: str) -> dict[str, Any] | None:
        checkpoint = self._checkpoints.get(checkpoint_id)
        return dict(checkpoint.state) if checkpoint is not None else None

    def restore(self, checkpoint_id: str) -> dict[str, Any]:
        state = self.load(checkpoint_id)
        if state is None:
            raise KeyError(f"unknown checkpoint {checkpoint_id!r}")
        return state

    def latest(self) -> Checkpoint | None:
        if not self._checkpoints:
            return None
        return self._checkpoints[max(sorted(self._checkpoints))]

    def list(self) -> list[Checkpoint]:
        return [self._checkpoints[cid] for cid in sorted(self._checkpoints)]

    def delete(self, checkpoint_id: str) -> bool:
        return self._checkpoints.pop(checkpoint_id, None) is not None
