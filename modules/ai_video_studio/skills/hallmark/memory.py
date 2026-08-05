"""Hallmark memory — in-memory key/value store for cross-run state."""
from __future__ import annotations
from typing import Any


class MemoryStore:
    """Simple in-memory store with get/set/keys/clear/snapshot."""

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def keys(self) -> list[str]:
        return list(self._data)

    def clear(self) -> None:
        self._data.clear()

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)
