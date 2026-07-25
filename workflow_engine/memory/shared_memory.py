from __future__ import annotations

from typing import Any


class SharedMemory:
    _instance: SharedMemory | None = None

    def __new__(cls) -> SharedMemory:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data: dict[str, dict[str, Any]] = {}
        return cls._instance

    def set(self, key: str, value: Any, namespace: str = "default") -> None:
        self._data.setdefault(namespace, {})[key] = value

    def get(self, key: str, namespace: str = "default") -> Any | None:
        return self._data.get(namespace, {}).get(key)

    def delete(self, key: str, namespace: str = "default") -> None:
        self._data.get(namespace, {}).pop(key, None)

    def clear_namespace(self, namespace: str) -> None:
        self._data.pop(namespace, None)

    def clear_all(self) -> None:
        self._data.clear()
