from __future__ import annotations

import time
from typing import Any

from .memory_types import (
    MemoryCategory,
    MemoryData,
    MemoryID,
    MemoryScope,
    MemoryStatus,
    Metadata,
    Tags,
    Timestamp,
)


class MemoryEntry:
    """A single entry in the memory store."""

    def __init__(
        self,
        key: MemoryID,
        data: MemoryData,
        scope: MemoryScope = MemoryScope.LOCAL,
        category: MemoryCategory = MemoryCategory.CONTEXT,
        status: MemoryStatus = MemoryStatus.ACTIVE,
        tags: Tags | None = None,
        metadata: Metadata | None = None,
        ttl: float | None = None,
        priority: int = 0,
        created_at: Timestamp | None = None,
        updated_at: Timestamp | None = None,
    ):
        now = time.time()
        self._key = key
        self._data = data
        self._scope = scope
        self._category = category
        self._status = status
        self._tags = tags or []
        self._metadata = metadata or {}
        self._ttl = ttl
        self._priority = priority
        self._created_at = created_at or now
        self._updated_at = updated_at or now
        self._access_count: int = 0

    @property
    def key(self) -> MemoryID:
        return self._key

    @property
    def data(self) -> MemoryData:
        self._access_count += 1
        return dict(self._data)

    @data.setter
    def data(self, value: MemoryData) -> None:
        self._data = value
        self._updated_at = time.time()

    @property
    def scope(self) -> MemoryScope:
        return self._scope

    @scope.setter
    def scope(self, value: MemoryScope) -> None:
        self._scope = value

    @property
    def category(self) -> MemoryCategory:
        return self._category

    @property
    def status(self) -> MemoryStatus:
        return self._status

    @status.setter
    def status(self, value: MemoryStatus) -> None:
        self._status = value

    @property
    def tags(self) -> Tags:
        return list(self._tags)

    @property
    def metadata(self) -> Metadata:
        return dict(self._metadata)

    @property
    def ttl(self) -> float | None:
        return self._ttl

    @property
    def priority(self) -> int:
        return self._priority

    @property
    def created_at(self) -> Timestamp:
        return self._created_at

    @property
    def updated_at(self) -> Timestamp:
        return self._updated_at

    @property
    def access_count(self) -> int:
        return self._access_count

    @property
    def is_expired(self) -> bool:
        if self._ttl is None:
            return False
        return time.time() > self._created_at + self._ttl

    @property
    def size_bytes(self) -> int:
        import json

        return len(json.dumps(self._data).encode("utf-8"))

    def touch(self) -> None:
        self._updated_at = time.time()
        self._access_count += 1

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self._key,
            "data": self._data,
            "scope": self._scope.name,
            "category": self._category.name,
            "status": self._status.name,
            "tags": list(self._tags),
            "metadata": dict(self._metadata),
            "ttl": self._ttl,
            "priority": self._priority,
            "created_at": self._created_at,
            "updated_at": self._updated_at,
            "access_count": self._access_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        return cls(
            key=data["key"],
            data=data.get("data", {}),
            scope=MemoryScope[data.get("scope", "LOCAL")],
            category=MemoryCategory[data.get("category", "CONTEXT")],
            status=MemoryStatus[data.get("status", "ACTIVE")],
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            ttl=data.get("ttl"),
            priority=data.get("priority", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )


class MemoryQuery:
    """Query parameters for searching memory entries."""

    def __init__(
        self,
        query: str = "",
        scope: MemoryScope | None = None,
        category: MemoryCategory | None = None,
        status: MemoryStatus | None = None,
        tags: Tags | None = None,
        min_priority: int = 0,
        max_results: int = 100,
        include_expired: bool = False,
    ):
        self._query = query
        self._scope = scope
        self._category = category
        self._status = status
        self._tags = tags or []
        self._min_priority = min_priority
        self._max_results = max_results
        self._include_expired = include_expired

    @property
    def query(self) -> str:
        return self._query

    @property
    def scope(self) -> MemoryScope | None:
        return self._scope

    @property
    def category(self) -> MemoryCategory | None:
        return self._category

    @property
    def status(self) -> MemoryStatus | None:
        return self._status

    @property
    def tags(self) -> Tags:
        return list(self._tags)

    @property
    def min_priority(self) -> int:
        return self._min_priority

    @property
    def max_results(self) -> int:
        return self._max_results

    @property
    def include_expired(self) -> bool:
        return self._include_expired

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self._query,
            "scope": self._scope.name if self._scope else None,
            "category": self._category.name if self._category else None,
            "status": self._status.name if self._status else None,
            "tags": list(self._tags),
            "min_priority": self._min_priority,
            "max_results": self._max_results,
            "include_expired": self._include_expired,
        }


class MemorySummary:
    """Summary statistics for the memory subsystem."""

    def __init__(
        self,
        total_entries: int = 0,
        total_size_bytes: int = 0,
        active_entries: int = 0,
        expired_entries: int = 0,
        by_scope: dict[str, int] | None = None,
        by_category: dict[str, int] | None = None,
    ):
        self._total_entries = total_entries
        self._total_size_bytes = total_size_bytes
        self._active_entries = active_entries
        self._expired_entries = expired_entries
        self._by_scope = by_scope or {}
        self._by_category = by_category or {}

    @property
    def total_entries(self) -> int:
        return self._total_entries

    @property
    def total_size_bytes(self) -> int:
        return self._total_size_bytes

    @property
    def active_entries(self) -> int:
        return self._active_entries

    @property
    def expired_entries(self) -> int:
        return self._expired_entries

    @property
    def by_scope(self) -> dict[str, int]:
        return dict(self._by_scope)

    @property
    def by_category(self) -> dict[str, int]:
        return dict(self._by_category)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_entries": self._total_entries,
            "total_size_bytes": self._total_size_bytes,
            "active_entries": self._active_entries,
            "expired_entries": self._expired_entries,
            "by_scope": dict(self._by_scope),
            "by_category": dict(self._by_category),
        }
