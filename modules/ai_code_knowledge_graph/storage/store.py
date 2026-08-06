"""Store interface — key/value persistence for knowledge artifacts.

Backends (JSON files, SQLite, later postgres/redis/neo4j) implement the same
small contract so snapshots, exports and caches stay swappable via config.
"""
from __future__ import annotations

from typing import Any, Protocol


class Store(Protocol):
    """Key/value persistence contract used by snapshots and exports."""

    def save(self, key: str, payload: dict[str, Any]) -> None:
        """Persist ``payload`` under ``key`` (upsert)."""
        ...

    def load(self, key: str) -> dict[str, Any] | None:
        """Return the payload for ``key`` or ``None`` when missing."""
        ...

    def delete(self, key: str) -> bool:
        """Remove ``key``; return ``True`` when it existed."""
        ...

    def exists(self, key: str) -> bool:
        """Return whether ``key`` is present."""
        ...

    def list_keys(self, prefix: str = "") -> list[str]:
        """Return stored keys (optionally filtered by prefix), sorted."""
        ...

    def clear(self) -> None:
        """Remove all stored keys."""
        ...
