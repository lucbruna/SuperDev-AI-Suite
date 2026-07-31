from __future__ import annotations

import logging
from typing import Any

from ..knowledge_interfaces import MemoryStore
from ..knowledge_models import MemoryRecord


class ProceduralMemory:
    """Stores reusable procedures and step-by-step playbooks."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.procedural")
        self._store = store

    def store_procedure(self, name: str, steps: list[str], metadata: dict[str, Any] | None = None) -> str:
        if self._store is None:
            raise RuntimeError("procedural memory requires a memory store")
        content = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(steps))
        record = MemoryRecord(
            content=content,
            memory_type="procedural",
            importance=0.9,
            metadata={"name": name, "steps": list(steps), **(metadata or {})},
        )
        return self._store.save(record)

    def procedures(self) -> list[MemoryRecord]:
        if self._store is None:
            return []
        return self._store.list("procedural")

    def get_procedure(self, name: str) -> list[str] | None:
        for record in self.procedures():
            if record.metadata.get("name") == name:
                return list(record.metadata.get("steps", []))
        return None

    def steps(self) -> int:
        return sum(len(record.metadata.get("steps", [])) for record in self.procedures())
