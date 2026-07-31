from __future__ import annotations

import time
from typing import Any


class CacheEntry:
    """A single cache entry with metadata."""

    def __init__(self, key: str, value: Any, ttl: float = 300.0) -> None:
        self._key = key
        self._value = value
        self._ttl = ttl
        self._created_at = time.time()
        self._accessed_at = self._created_at
        self._access_count: int = 1

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> Any:
        self._accessed_at = time.time()
        self._access_count += 1
        return self._value

    @value.setter
    def value(self, val: Any) -> None:
        self._value = val
        self._accessed_at = time.time()

    @property
    def ttl(self) -> float:
        return self._ttl

    @property
    def created_at(self) -> float:
        return self._created_at

    @property
    def accessed_at(self) -> float:
        return self._accessed_at

    @property
    def access_count(self) -> int:
        return self._access_count

    @property
    def is_expired(self) -> bool:
        return time.time() > self._created_at + self._ttl

    @property
    def age(self) -> float:
        return time.time() - self._created_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self._key,
            "value": self._value,
            "ttl": self._ttl,
            "created_at": self._created_at,
            "accessed_at": self._accessed_at,
            "access_count": self._access_count,
            "expired": self.is_expired,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CacheEntry:
        entry = cls(data["key"], data["value"], data["ttl"])
        entry._created_at = data.get("created_at", entry._created_at)
        entry._accessed_at = data.get("accessed_at", entry._accessed_at)
        entry._access_count = data.get("access_count", entry._access_count)
        return entry
