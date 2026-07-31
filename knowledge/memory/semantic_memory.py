from __future__ import annotations

import logging
from typing import Any

from ..knowledge_interfaces import MemoryStore
from ..knowledge_models import MemoryRecord


class SemanticMemory:
    """Stores facts, concepts, and general knowledge about the domain."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.semantic")
        self._store = store

    def store_fact(self, fact: str, subject: str = "", metadata: dict[str, Any] | None = None) -> str:
        if self._store is None:
            raise RuntimeError("semantic memory requires a memory store")
        record = MemoryRecord(
            content=fact,
            memory_type="semantic",
            importance=0.8,
            metadata={"subject": subject, **(metadata or {})},
        )
        return self._store.save(record)

    def facts(self, subject: str | None = None) -> list[MemoryRecord]:
        if self._store is None:
            return []
        records = self._store.list("semantic")
        if subject:
            records = [r for r in records if r.metadata.get("subject") == subject]
        return records

    def query(self, text: str) -> list[str]:
        lowered = text.lower()
        return [r.content for r in self.facts() if lowered in r.content.lower() or r.content.lower() in lowered]
