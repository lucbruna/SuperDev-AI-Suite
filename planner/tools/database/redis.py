from __future__ import annotations

from typing import Any


class Redis:
    """Redis in-memory data structure adapter."""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self.host = host
        self.port = port
        self.db = db
        self._store: dict[str, Any] = {}

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._store.clear()
        self._connected = False

    def get(self, key: str) -> Any:
        return self._store.get(key)

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        self._store[key] = value

    def delete(self, key: str) -> int:
        return 1 if self._store.pop(key, None) is not None else 0

    def exists(self, key: str) -> bool:
        return key in self._store

    def publish(self, channel: str, message: str) -> int:
        return 1

    def subscribe(self, channel: str) -> list[str]:
        return []
