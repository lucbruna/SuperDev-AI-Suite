"""Model memory management."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class ModelMemory:
    def __init__(self, max_size: int = 10000) -> None:
        self._memories: List[Dict[str, Any]] = []
        self._max_size = max_size
    def store(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        entry = {"key": key, "value": value, "metadata": metadata or {}, "created_at": time.time(), "access_count": 0}
        self._memories.append(entry)
        if len(self._memories) > self._max_size:
            self._memories = self._memories[-self._max_size:]
        return entry
    def retrieve(self, key: str) -> Optional[Any]:
        for m in reversed(self._memories):
            if m["key"] == key:
                m["access_count"] += 1
                m["last_accessed"] = time.time()
                return m["value"]
        return None
    def search(self, query: str) -> List[Dict[str, Any]]:
        return [m for m in self._memories if query.lower() in str(m.get("key", "")).lower() or query.lower() in str(m.get("value", "")).lower()]
    def recent(self, count: int = 10) -> List[Dict[str, Any]]:
        return self._memories[-count:]
    def delete(self, key: str) -> bool:
        original_len = len(self._memories)
        self._memories = [m for m in self._memories if m["key"] != key]
        return len(self._memories) < original_len
    def clear(self) -> int:
        n = len(self._memories)
        self._memories.clear()
        return n
    def count(self) -> int:
        return len(self._memories)
    def most_accessed(self, count: int = 5) -> List[Dict[str, Any]]:
        return sorted(self._memories, key=lambda m: m.get("access_count", 0), reverse=True)[:count]
