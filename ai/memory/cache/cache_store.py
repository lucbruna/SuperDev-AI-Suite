from __future__ import annotations

from typing import Any, Dict, List, Optional

from .cache_entry import CacheEntry
from .cache_policy import CachePolicy


class CacheStore:
    """Base cache store implementation."""

    def __init__(self, name: str, policy: Optional[CachePolicy] = None) -> None:
        self._name = name
        self._policy = policy or CachePolicy()
        self._entries: Dict[str, CacheEntry] = {}

    @property
    def name(self) -> str:
        return self._name

    @property
    def size(self) -> int:
        return len(self._entries)

    @property
    def policy(self) -> CachePolicy:
        return self._policy

    def get(self, key: str) -> Optional[Any]:
        entry = self._entries.get(key)
        if entry is None or entry.is_expired:
            if entry:
                del self._entries[key]
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl: float = 300.0) -> None:
        if self._policy.should_evict(self.size):
            self._evict()
        self._entries[key] = CacheEntry(key, value, ttl)

    def delete(self, key: str) -> bool:
        if key in self._entries:
            del self._entries[key]
            return True
        return False

    def clear(self) -> None:
        self._entries.clear()

    def keys(self) -> List[str]:
        return list(self._entries.keys())

    def _evict(self) -> None:
        if not self._entries:
            return
        entries_data = [e.to_dict() for e in self._entries.values()]
        victim = self._policy.select_victim(entries_data)
        self._entries.pop(victim, None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "size": self.size,
            "keys": self.keys(),
        }
