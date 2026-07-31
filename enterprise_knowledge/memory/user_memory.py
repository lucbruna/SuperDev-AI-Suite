"""User memory: per-owner profiles, preferences and history."""

from __future__ import annotations

import time
from typing import Any

from enterprise_knowledge.knowledge_models import MemoryRecord, MemoryType
from enterprise_knowledge.knowledge_protocols import new_id


class UserMemory:
    """Personalized memory keyed by owner id."""

    def __init__(self) -> None:
        self._preferences: dict[str, dict[str, Any]] = {}
        self._entries: dict[str, MemoryRecord] = {}

    def set_preference(self, owner_id: str, key: str, value: Any) -> None:
        preferences = self._preferences.setdefault(owner_id, {})
        preferences[key] = value

    def get_preference(self, owner_id: str, key: str,
                       default: Any = None) -> Any:
        return self._preferences.get(owner_id, {}).get(key, default)

    def remember(self, owner_id: str, content: str,
                 metadata: dict[str, Any] | None = None) -> MemoryRecord:
        record = MemoryRecord(memory_id=new_id("memory"),
                              memory_type=MemoryType.LONG_TERM,
                              content=content, owner_id=owner_id,
                              metadata=dict(metadata or {}),
                              created_at=time.time())
        self._entries[record.memory_id] = record
        return record

    def recall(self, owner_id: str, limit: int = 10) -> list[MemoryRecord]:
        entries = [rec for rec in self._entries.values()
                   if rec.owner_id == owner_id]
        entries.sort(key=lambda rec: rec.created_at, reverse=True)
        return entries[:max(0, limit)]

    def knows(self, owner_id: str) -> bool:
        return owner_id in self._preferences or any(
            rec.owner_id == owner_id for rec in self._entries.values())

    def count(self) -> int:
        return len(self._entries)
