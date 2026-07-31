"""Short-term memory: recent, fast-forgetting items."""

from __future__ import annotations

import time
from typing import Any

from enterprise_knowledge.knowledge_models import MemoryRecord, MemoryType
from enterprise_knowledge.knowledge_protocols import new_id


class ShortTermMemory:
    """Holds recent items; drops oldest beyond capacity or TTL."""

    def __init__(self, capacity: int = 20, ttl_seconds: float = 3600.0) -> None:
        self.capacity = max(1, capacity)
        self.ttl_seconds = ttl_seconds
        self._items: dict[str, MemoryRecord] = {}
        self._seq = 0
        self._order: dict[str, int] = {}

    def remember(self, content: str, owner_id: str = "",
                 metadata: dict[str, Any] | None = None) -> MemoryRecord:
        self._evict()
        record = MemoryRecord(memory_id=new_id("memory"),
                              memory_type=MemoryType.SHORT_TERM,
                              content=content, owner_id=owner_id,
                              metadata=dict(metadata or {}),
                              created_at=time.time())
        self._items[record.memory_id] = record
        self._seq += 1
        self._order[record.memory_id] = self._seq
        return record

    def _evict(self) -> None:
        now = time.time()
        self._items = {
            mid: rec for mid, rec in self._items.items()
            if now - rec.created_at <= self.ttl_seconds
        }
        while len(self._items) > self.capacity:
            oldest = min(self._items.values(),
                         key=lambda rec: (rec.created_at,
                                          self._order.get(rec.memory_id, 0)))
            self._items.pop(oldest.memory_id, None)
            self._order.pop(oldest.memory_id, None)

    def recall(self, limit: int = 5) -> list[MemoryRecord]:
        self._evict()
        ordered = sorted(self._items.values(),
                         key=lambda rec: (rec.created_at,
                                          self._order.get(rec.memory_id, 0)),
                         reverse=True)
        return ordered[:max(0, limit)]

    def recall_containing(self, term: str) -> list[MemoryRecord]:
        term = term.lower()
        return [rec for rec in self._items.values()
                if term in rec.content.lower()]

    def count(self) -> int:
        self._evict()
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()
        self._order.clear()
