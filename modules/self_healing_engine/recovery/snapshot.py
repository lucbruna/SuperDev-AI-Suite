"""Snapshots: checkpoints of state with bounded retention and persistence."""
from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from modules.self_healing_engine.config.recovery_config import RecoveryConfig
from modules.self_healing_engine.core.healing_context import HealingContext


class SnapshotRecoveryError(RuntimeError):
    """Raised on snapshot persistence failures."""


@dataclass(slots=True)
class Snapshot:
    """A point-in-time checkpoint of healing state."""

    id: str
    kind: str
    data: dict[str, object] = field(default_factory=dict)
    sequence: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "kind": self.kind,
            "data": self.data,
            "sequence": self.sequence,
        }


class SnapshotManager:
    """Creates and retrieves snapshots with bounded retention."""

    def __init__(self, recovery_config: RecoveryConfig | None = None) -> None:
        self._config = recovery_config or RecoveryConfig()
        self._snapshots: list[Snapshot] = []
        self._sequence = 0

    @property
    def max_checkpoints(self) -> int:
        return self._config.max_checkpoints

    def create(
        self,
        kind: str,
        ctx: HealingContext,
        data: dict[str, object] | None = None,
    ) -> Snapshot:
        self._sequence += 1
        snapshot = Snapshot(
            id=f"{kind}-{self._sequence}",
            kind=kind,
            data=data or {},
            sequence=self._sequence,
        )
        self._snapshots.append(snapshot)
        while len(self._snapshots) > self.max_checkpoints:
            self._snapshots.pop(0)
        ctx.publish(
            "recovery.snapshot_created",
            {"id": snapshot.id, "kind": snapshot.kind},
        )
        return snapshot

    def list(self) -> list[Snapshot]:
        return list(reversed(self._snapshots))

    def latest(self, kind: str | None = None) -> Snapshot | None:
        for snapshot in reversed(self._snapshots):
            if kind is None or snapshot.kind == kind:
                return snapshot
        return None

    def load(self, snapshot_id: str) -> Snapshot:
        for snapshot in self._snapshots:
            if snapshot.id == snapshot_id:
                return snapshot
        raise KeyError(f"snapshot not found: {snapshot_id}")

    def save_all(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = [s.to_dict() for s in self._snapshots]
        fd, tmp = tempfile.mkstemp(dir=str(target.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, ensure_ascii=False, indent=2)
            os.replace(tmp, target)
        except OSError as exc:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise SnapshotRecoveryError(f"failed to save snapshots: {exc}") from exc

    def load_all(self, path: str | Path) -> None:
        target = Path(path)
        if not target.exists():
            return
        try:
            with target.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise SnapshotRecoveryError(f"failed to load snapshots: {exc}") from exc
        self._snapshots = [
            Snapshot(
                id=item["id"],
                kind=item["kind"],
                data=item.get("data") or {},
                sequence=int(item.get("sequence", 0)),
            )
            for item in payload
            if isinstance(item, dict)
        ]
        self._sequence = max((s.sequence for s in self._snapshots), default=0)
