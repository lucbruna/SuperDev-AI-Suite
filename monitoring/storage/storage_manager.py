from __future__ import annotations

import logging
from typing import Any, Protocol


class StorageBackend(Protocol):
    def store(self, key: str, data: dict[str, Any]) -> None: ...
    def retrieve(self, key: str) -> dict[str, Any] | None: ...
    def delete(self, key: str) -> bool: ...
    def list_keys(self) -> list[str]: ...
    def close(self) -> None: ...


class StorageManager:
    """Manages storage backends for monitoring data."""

    def __init__(self, backend: StorageBackend | None = None) -> None:
        self._backend = backend
        self._logger = logging.getLogger("superdev.storage")

    @property
    def backend(self) -> StorageBackend | None:
        return self._backend

    @backend.setter
    def backend(self, backend: StorageBackend) -> None:
        self._backend = backend

    def store(self, key: str, data: dict[str, Any]) -> None:
        if self._backend is None:
            self._logger.error("No storage backend configured")
            return
        try:
            self._backend.store(key, data)
        except Exception as e:
            self._logger.error("Storage write failed: %s", e)

    def retrieve(self, key: str) -> dict[str, Any] | None:
        if self._backend is None:
            self._logger.error("No storage backend configured")
            return None
        try:
            return self._backend.retrieve(key)
        except Exception as e:
            self._logger.error("Storage read failed: %s", e)
            return None

    def delete(self, key: str) -> bool:
        if self._backend is None:
            return False
        try:
            return self._backend.delete(key)
        except Exception as e:
            self._logger.error("Storage delete failed: %s", e)
            return False

    def list_keys(self) -> list[str]:
        if self._backend is None:
            return []
        try:
            return self._backend.list_keys()
        except Exception as e:
            self._logger.error("Storage list failed: %s", e)
            return []
