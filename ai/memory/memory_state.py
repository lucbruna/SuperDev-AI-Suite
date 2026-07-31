from __future__ import annotations

import time
from enum import Enum, auto
from typing import Any

from .memory_types import MemoryStatus


class MemoryPhase(Enum):
    """High-level lifecycle phases of the memory subsystem."""

    UNINITIALIZED = auto()
    INITIALIZING = auto()
    READY = auto()
    MAINTENANCE = auto()
    BACKING_UP = auto()
    RESTORING = auto()
    CONSOLIDATING = auto()
    ERROR = auto()
    SHUTDOWN = auto()


class MemoryState:
    """State manager for the memory subsystem lifecycle."""

    def __init__(self):
        self._phase: MemoryPhase = MemoryPhase.UNINITIALIZED
        self._statuses: dict[str, MemoryStatus] = {}
        self._errors: list[dict[str, Any]] = []
        self._started_at: float | None = None
        self._last_maintenance: float | None = None
        self._last_backup: float | None = None
        self._last_consolidation: float | None = None

    @property
    def phase(self) -> MemoryPhase:
        return self._phase

    @property
    def is_ready(self) -> bool:
        return self._phase == MemoryPhase.READY

    @property
    def started_at(self) -> float | None:
        return self._started_at

    @property
    def last_maintenance(self) -> float | None:
        return self._last_maintenance

    @property
    def last_backup(self) -> float | None:
        return self._last_backup

    @property
    def last_consolidation(self) -> float | None:
        return self._last_consolidation

    @property
    def errors(self) -> list[dict[str, Any]]:
        return list(self._errors)

    def transition_to(self, phase: MemoryPhase) -> None:
        self._phase = phase
        if phase == MemoryPhase.READY and self._started_at is None:
            self._started_at = time.time()

    def set_status(self, key: str, status: MemoryStatus) -> None:
        self._statuses[key] = status

    def get_status(self, key: str) -> MemoryStatus | None:
        return self._statuses.get(key)

    def record_maintenance(self) -> None:
        self._last_maintenance = time.time()

    def record_backup(self) -> None:
        self._last_backup = time.time()

    def record_consolidation(self) -> None:
        self._last_consolidation = time.time()

    def record_error(self, error: str, details: dict[str, Any] | None = None) -> None:
        self._errors.append(
            {
                "error": error,
                "details": details or {},
                "timestamp": time.time(),
            }
        )

    def clear_errors(self) -> None:
        self._errors.clear()

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self._phase.name,
            "is_ready": self.is_ready,
            "started_at": self._started_at,
            "last_maintenance": self._last_maintenance,
            "last_backup": self._last_backup,
            "last_consolidation": self._last_consolidation,
            "error_count": len(self._errors),
        }
