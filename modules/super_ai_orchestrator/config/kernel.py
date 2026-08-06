"""Kernel configuration: queue and scheduling behaviour."""
from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from typing import Any

from modules.super_ai_orchestrator.config.base import apply_overrides


@dataclass(slots=True)
class KernelConfig:
    """Controls the deterministic scheduling kernel.

    Attributes:
        slices_per_tick: how many task work-slices one ``tick()`` processes.
        queue_capacity: maximum number of queued tasks (soft cap).
        dedupe_enabled: skip tasks identical (kind + title + payload) to a
            task already queued or running.
        min_priority: lowest allowed priority (1 = least urgent).
        max_priority: highest allowed priority (10 = most urgent).
        max_concurrent: how many tasks may run at the same time.
        governance_required: whether submitted tasks must pass the approval
            gate before execution.
        rollback_on_failure: whether a failed task automatically triggers
            rollback of its recorded mutations.
    """

    slices_per_tick: int = 3
    queue_capacity: int = 256
    dedupe_enabled: bool = True
    min_priority: int = 1
    max_priority: int = 10
    max_concurrent: int = 4
    governance_required: bool = True
    rollback_on_failure: bool = False

    def resolve(self, overrides: dict[str, Any] | None = None) -> "KernelConfig":
        return apply_overrides(self, overrides)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "KernelConfig":
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})
