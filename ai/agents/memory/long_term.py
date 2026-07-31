"""Long-term persistent memory with importance decay."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class LongTermMemory:
    """Persistent memory with importance scoring and access-based retention."""

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, Any]] = {}
        self._access_counts: Dict[str, int] = {}

    def store(self, key: str, value: Any, importance: float = 0.5) -> None:
        self._store[key] = {
            "value": value,
            "importance": max(0.0, min(1.0, importance)),
            "created_at": time.time(),
            "last_accessed": time.time(),
        }
        self._access_counts[key] = self._access_counts.get(key, 0) + 1

    def retrieve(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        entry["last_accessed"] = time.time()
        self._access_counts[key] = self._access_counts.get(key, 0) + 1
        return entry.get("value")

    def remove(self, key: str) -> bool:
        removed = key in self._store
        self._store.pop(key, None)
        self._access_counts.pop(key, None)
        return removed

    def contains(self, key: str) -> bool:
        return key in self._store

    def count(self) -> int:
        return len(self._store)

    def get_all(self) -> Dict[str, Any]:
        return {k: v.get("value") for k, v in self._store.items()}

    def keys(self) -> List[str]:
        return list(self._store.keys())

    def get_by_importance(self, min_importance: float = 0.0,
                          max_importance: float = 1.0) -> Dict[str, Any]:
        result = {}
        for k, v in self._store.items():
            imp = v.get("importance", 0.5)
            if min_importance <= imp <= max_importance:
                result[k] = v.get("value")
        return result

    def get_most_accessed(self, limit: int = 10) -> List[str]:
        sorted_keys = sorted(
            self._access_counts.keys(),
            key=lambda k: self._access_counts.get(k, 0),
            reverse=True,
        )
        return sorted_keys[:limit]

    def clear(self) -> None:
        self._store.clear()
        self._access_counts.clear()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "count": len(self._store),
            "keys": list(self._store.keys()),
            "access_counts": dict(self._access_counts),
        }
