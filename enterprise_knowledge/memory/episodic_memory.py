"""Episodic memory: timestamped event sequences (what happened when)."""

from __future__ import annotations

import time
from typing import Any

from enterprise_knowledge.knowledge_models import MemoryRecord, MemoryType
from enterprise_knowledge.knowledge_protocols import new_id


class EpisodicMemory:
    """Stores episodes (structured events) with context and ordering."""

    def __init__(self, capacity: int = 100) -> None:
        self.capacity = max(1, capacity)
        self._episodes: dict[str, MemoryRecord] = {}
        self._seq = 0
        self._order: dict[str, int] = {}

    def remember_event(self, action: str, actor: str = "",
                       context: str = "",
                       metadata: dict[str, Any] | None = None) -> MemoryRecord:
        content = f"{action} por {actor}" if actor else action
        meta = dict(metadata or {})
        meta["context"] = context
        meta["action"] = action
        meta["actor"] = actor
        record = MemoryRecord(memory_id=new_id("memory"),
                              memory_type=MemoryType.EPISODIC,
                              content=content, owner_id=actor,
                              metadata=meta, created_at=time.time())
        self._episodes[record.memory_id] = record
        self._seq += 1
        self._order[record.memory_id] = self._seq
        if len(self._episodes) > self.capacity:
            oldest = min(self._episodes.values(),
                         key=lambda rec: (rec.created_at,
                                          self._order.get(rec.memory_id, 0)))
            self._episodes.pop(oldest.memory_id, None)
            self._order.pop(oldest.memory_id, None)
        return record

    def timeline(self, limit: int = 10) -> list[MemoryRecord]:
        ordered = sorted(self._episodes.values(),
                         key=lambda rec: (rec.created_at,
                                          self._order.get(rec.memory_id, 0)),
                         reverse=True)
        return ordered[:max(0, limit)]

    def events_by_actor(self, actor: str) -> list[MemoryRecord]:
        return [rec for rec in self._episodes.values()
                if rec.owner_id == actor]

    def count(self) -> int:
        return len(self._episodes)

    def clear(self) -> None:
        self._episodes.clear()
        self._order.clear()
