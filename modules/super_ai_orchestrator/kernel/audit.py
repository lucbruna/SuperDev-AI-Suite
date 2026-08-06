"""AuditTrail — an immutable, append-only record of orchestrator actions.

Every state change in the kernel is recorded here. Records are frozen and
never mutated after creation; the trail exposes a read-only tuple view.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """One audit entry.

    Attributes:
        seq: monotonic record order.
        kind: what happened (e.g. ``submit``, ``transition``, ``cancel``).
        task_seq: seq of the affected task (``-1`` for kernel-level events).
        detail: structured context (from/to status, reason, ...).
    """

    seq: int
    kind: str
    task_seq: int = -1
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AuditTrail:
    """Append-only audit log with deterministic order."""

    records: list[AuditRecord] = field(default_factory=list)

    def record(
        self,
        kind: str,
        task_seq: int = -1,
        detail: dict[str, Any] | None = None,
    ) -> AuditRecord:
        entry = AuditRecord(
            seq=len(self.records),
            kind=kind,
            task_seq=task_seq,
            detail=detail or {},
        )
        self.records.append(entry)
        return entry

    def all(self) -> tuple[AuditRecord, ...]:
        return tuple(self.records)

    def for_task(self, task_seq: int) -> tuple[AuditRecord, ...]:
        return tuple(r for r in self.records if r.task_seq == task_seq)

    def kinds(self) -> tuple[str, ...]:
        return tuple(r.kind for r in self.records)

    def to_dict(self) -> list[dict[str, Any]]:
        return [r.to_dict() for r in self.records]
