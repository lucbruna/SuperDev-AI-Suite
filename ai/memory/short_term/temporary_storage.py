from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class TempEntry:
    """A single entry in temporary storage."""

    def __init__(self, key: str, value: Any, ttl: float | None = None):
        self._key = key
        self._value = value
        self._ttl = ttl
        self._created_at = time.time()

    @property
    def key(self) -> str:
        return self._key

    @property
    def value(self) -> Any:
        return self._value

    @property
    def ttl(self) -> float | None:
        return self._ttl

    @property
    def is_expired(self) -> bool:
        if self._ttl is None:
            return False
        return time.time() > self._created_at + self._ttl

    @property
    def age(self) -> float:
        return time.time() - self._created_at


class TemporaryStorage:
    """Ephemeral key-value storage with optional TTL."""

    def __init__(self, default_ttl: float = 300.0):
        self._default_ttl = default_ttl
        self._entries: Dict[str, TempEntry] = {}

    @property
    def default_ttl(self) -> float:
        return self._default_ttl

    @property
    def count(self) -> int:
        return len(self._entries)

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        self._entries[key] = TempEntry(key, value, ttl)

    def get(self, key: str) -> Any | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        if entry.is_expired:
            del self._entries[key]
            return None
        return entry.value

    def delete(self, key: str) -> bool:
        return self._entries.pop(key, None) is not None

    def has(self, key: str) -> bool:
        entry = self._entries.get(key)
        if entry is None:
            return False
        if entry.is_expired:
            del self._entries[key]
            return False
        return True

    def keys(self) -> List[str]:
        return list(self._entries.keys())

    def clear(self) -> None:
        self._entries.clear()

    def purge_expired(self) -> int:
        expired = [k for k, v in self._entries.items() if v.is_expired]
        for k in expired:
            del self._entries[k]
        return len(expired)
