"""Long-term memory: persistent, importance-weighted items."""

from __future__ import annotations

import time
from typing import Any

from enterprise_knowledge.knowledge_models import MemoryRecord, MemoryType
from enterprise_knowledge.knowledge_protocols import new_id


class LongTermMemory:
    """Keeps items indefinitely, weighted by importance and access."""

    def __init__(self, decay: float = 0.01) -> None:
        self.decay = decay
        self._items: dict[str, MemoryRecord] = {}

    def remember(self, content: str, owner_id: str = "",
                 importance: float = 0.5,
                 metadata: dict[str, Any] | None = None) -> MemoryRecord:
        record = MemoryRecord(memory_id=new_id("memory"),
                              memory_type=MemoryType.LONG_TERM,
                              content=content, owner_id=owner_id,
                              metadata=dict(metadata or {}),
                              importance=max(0.0, min(1.0, importance)),
                              created_at=time.time())
        self._items[record.memory_id] = record
        return record

    def recall(self, limit: int = 5,
               min_importance: float = 0.0) -> list[MemoryRecord]:
        now = time.time()
        ranked = []
        for record in self._items.values():
            if record.importance < min_importance:
                continue
            age = max(0.0, now - record.created_at)
            score = record.importance + self.decay * record.access_count \
                - self.decay * age / 3600.0
            record.access_count += 1
            record.last_accessed_at = now
            ranked.append((score, record))
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [record for _, record in ranked[:max(0, limit)]]

    def recall_containing(self, term: str) -> list[MemoryRecord]:
        term = term.lower()
        return [rec for rec in self._items.values()
                if term in rec.content.lower()]

    def count(self) -> int:
        return len(self._items)

    def clear(self) -> None:
        self._items.clear()
