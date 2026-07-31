"""Failover management for recovery (Volume 37, Fase 5)."""

from __future__ import annotations


class FailoverManager:
    """Tracks active failover pairs between primary and standby."""

    def __init__(self) -> None:
        self._active: dict[str, str] = {}

    def activate(self, primary: str, standby: str) -> bool:
        self._active[primary] = standby
        return True

    def failback(self, primary: str) -> bool:
        return self._active.pop(primary, None) is not None

    def standby_for(self, primary: str) -> str | None:
        return self._active.get(primary)

    def active_count(self) -> int:
        return len(self._active)
