"""StateMirror: timestamped snapshots of entity state with diff support."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from aios.digital_twin.entity import TwinEntity


@dataclass
class Snapshot:
    seq: int
    entity_id: str
    state: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"seq": self.seq, "entity_id": self.entity_id, "state": dict(self.state)}


class StateMirror:
    """Records one snapshot per entity per tick in deterministic seq order."""

    def __init__(self) -> None:
        self._snapshots: list[Snapshot] = []
        self._seq = 0

    def record(self, entity: TwinEntity) -> Snapshot:
        self._seq += 1
        snapshot = Snapshot(seq=self._seq, entity_id=entity.entity_id, state=dict(entity.state))
        self._snapshots.append(snapshot)
        return snapshot

    def history(self, entity_id: str) -> list[Snapshot]:
        return [snapshot for snapshot in self._snapshots if snapshot.entity_id == entity_id]

    def latest(self, entity_id: str) -> Optional[Snapshot]:
        history = self.history(entity_id)
        return history[-1] if history else None

    def diff(self, entity_id: str, from_seq: int, to_seq: int) -> dict[str, tuple[Any, Any]]:
        """Return {key: (old, new)} for keys that changed between snapshots."""
        history = self.history(entity_id)
        by_seq = {snapshot.seq: snapshot for snapshot in history}
        before = by_seq.get(from_seq)
        after = by_seq.get(to_seq)
        if before is None or after is None:
            raise KeyError(f"snapshot range {from_seq}->{to_seq} unavailable for {entity_id!r}")
        changed: dict[str, tuple[Any, Any]] = {}
        keys = set(before.state) | set(after.state)
        for key in sorted(keys):
            old = before.state.get(key)
            new = after.state.get(key)
            if old != new:
                changed[key] = (old, new)
        return changed

    def count(self) -> int:
        return len(self._snapshots)

    def snapshot(self) -> dict[str, Any]:
        return {
            "seq": self._seq,
            "snapshots": self.count(),
            "entities": sorted({snapshot.entity_id for snapshot in self._snapshots}),
        }
