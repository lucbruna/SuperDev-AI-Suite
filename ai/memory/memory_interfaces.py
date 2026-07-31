from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .memory_types import MemoryData, MemoryID, MemoryScope


class MemoryStorage(ABC):
    """Abstract interface for memory storage backends."""

    @abstractmethod
    async def store(self, key: MemoryID, data: MemoryData, scope: MemoryScope = MemoryScope.LOCAL) -> None: ...

    @abstractmethod
    async def retrieve(self, key: MemoryID) -> MemoryData | None: ...

    @abstractmethod
    async def update(self, key: MemoryID, data: MemoryData) -> bool: ...

    @abstractmethod
    async def delete(self, key: MemoryID) -> bool: ...

    @abstractmethod
    async def exists(self, key: MemoryID) -> bool: ...

    @abstractmethod
    async def search(self, query: str, scope: MemoryScope | None = None) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def clear(self, scope: MemoryScope | None = None) -> None: ...

    @abstractmethod
    async def size(self) -> int: ...


class MemorySerializer(ABC):
    """Abstract interface for memory serialization."""

    @abstractmethod
    def serialize(self, data: MemoryData) -> bytes: ...

    @abstractmethod
    def deserialize(self, raw: bytes) -> MemoryData: ...


class MemoryCacheBackend(ABC):
    """Abstract interface for cache backends."""

    @abstractmethod
    async def get(self, key: str) -> Any | None: ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: float | None = None) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> bool: ...

    @abstractmethod
    async def clear(self) -> None: ...

    @abstractmethod
    async def has(self, key: str) -> bool: ...


class MemoryEventHandler(ABC):
    """Abstract interface for handling memory events."""

    @abstractmethod
    async def handle_event(self, event_type: str, data: dict[str, Any]) -> None: ...


class MemoryObserver(ABC):
    """Abstract interface for observing memory operations."""

    @abstractmethod
    async def on_store(self, key: MemoryID, data: MemoryData) -> None: ...

    @abstractmethod
    async def on_retrieve(self, key: MemoryID, data: MemoryData | None) -> None: ...

    @abstractmethod
    async def on_delete(self, key: MemoryID) -> None: ...

    @abstractmethod
    async def on_clear(self) -> None: ...


class MemoryConsolidator(ABC):
    """Abstract interface for memory consolidation."""

    @abstractmethod
    async def consolidate(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]: ...


class MemoryEvictionPolicy(ABC):
    """Abstract interface for eviction policies."""

    @abstractmethod
    async def select_eviction_candidates(self, entries: list[dict[str, Any]], target_count: int) -> list[str]: ...


class MemoryCheckpointer(ABC):
    """Abstract interface for checkpoint operations."""

    @abstractmethod
    async def save_checkpoint(self, state: dict[str, Any]) -> str: ...

    @abstractmethod
    async def load_checkpoint(self, checkpoint_id: str) -> dict[str, Any] | None: ...


class MemoryBackuper(ABC):
    """Abstract interface for backup operations."""

    @abstractmethod
    async def create_backup(self, scope: MemoryScope | None = None) -> str: ...

    @abstractmethod
    async def restore_backup(self, backup_id: str) -> bool: ...

    @abstractmethod
    async def list_backups(self) -> list[dict[str, Any]]: ...
