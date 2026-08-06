"""Snapshots and diffs for the Digital Twin module."""
from __future__ import annotations

from dataclasses import dataclass, field

from modules.digital_twin.twin_engine.digital_twin_builder import TwinModel


@dataclass(slots=True)
class TwinSnapshot:
    """Immutable capture of a twin at a point in time."""

    twin_name: str
    sequence: int
    entities: dict[str, dict[str, object]] = field(default_factory=dict)
    relationships: list[dict[str, str]] = field(default_factory=list)
    meta: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_model(cls, model: TwinModel, sequence: int) -> "TwinSnapshot":
        return cls(
            twin_name=model.name,
            sequence=sequence,
            entities={k: dict(v) for k, v in model.entities.items()},
            relationships=[dict(r) for r in model.relationships],
            meta=dict(model.meta),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "twin_name": self.twin_name,
            "sequence": self.sequence,
            "entities": {k: dict(v) for k, v in self.entities.items()},
            "relationships": [dict(r) for r in self.relationships],
            "meta": dict(self.meta),
        }


@dataclass(slots=True)
class SnapshotDiff:
    """Entity-level differences between two snapshots."""

    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed)

    @property
    def has_changes(self) -> bool:
        return self.total > 0

    def to_dict(self) -> dict[str, object]:
        return {
            "added": list(self.added),
            "removed": list(self.removed),
            "changed": list(self.changed),
            "total": self.total,
        }


def diff_snapshots(before: TwinSnapshot, after: TwinSnapshot) -> SnapshotDiff:
    """Compare entity dicts by id between two snapshots."""
    before_ids = set(before.entities)
    after_ids = set(after.entities)
    diff = SnapshotDiff(
        added=sorted(after_ids - before_ids),
        removed=sorted(before_ids - after_ids),
    )
    changed = []
    for entity_id in sorted(after_ids & before_ids):
        if before.entities[entity_id] != after.entities[entity_id]:
            changed.append(entity_id)
    diff.changed = changed
    return diff


class TwinSnapshotter:
    """Produces monotonic snapshots from a twin model."""

    def __init__(self) -> None:
        self._sequence = 0

    def capture(self, model: TwinModel) -> TwinSnapshot:
        self._sequence += 1
        return TwinSnapshot.from_model(model, self._sequence)

    @property
    def sequence(self) -> int:
        return self._sequence
