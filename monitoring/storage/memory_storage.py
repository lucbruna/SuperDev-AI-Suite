from __future__ import annotations

from typing import Any


class MemoryStorage:
    """In-memory storage backend for monitoring data."""

    def __init__(self) -> None:
        self._data: dict[str, dict[str, Any]] = {}

    def store(self, key: str, data: dict[str, Any]) -> None:
        self._data[key] = data

    def retrieve(self, key: str) -> dict[str, Any] | None:
        return self._data.get(key)

    def delete(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            return True
        return False

    def list_keys(self) -> list[str]:
        return list(self._data.keys())

    def close(self) -> None:
        self._data.clear()

    def __len__(self) -> int:
        return len(self._data)
