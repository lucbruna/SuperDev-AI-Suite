from __future__ import annotations

import logging
from typing import Any

from ..knowledge_interfaces import MemoryStore
from ..knowledge_models import MemoryRecord


class EpisodicMemory:
    """Stores experiences: problems encountered and the solutions that worked."""

    def __init__(self, store: MemoryStore | None = None) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.episodic")
        self._store = store

    def record_experience(self, problem: str, solution: str, outcome: str = "success",
                          metadata: dict[str, Any] | None = None) -> str:
        if self._store is None:
            raise RuntimeError("episodic memory requires a memory store")
        content = f"Problem: {problem}\nSolution: {solution}\nOutcome: {outcome}"
        record = MemoryRecord(
            content=content,
            memory_type="episodic",
            importance=1.0 if outcome == "success" else 0.6,
            metadata={"problem": problem, "solution": solution, "outcome": outcome, **(metadata or {})},
        )
        return self._store.save(record)

    def experiences(self, outcome: str | None = None) -> list[MemoryRecord]:
        if self._store is None:
            return []
        records = self._store.list("episodic")
        if outcome:
            records = [r for r in records if r.metadata.get("outcome") == outcome]
        records.sort(key=lambda r: r.importance, reverse=True)
        return records

    def find_solution(self, problem: str) -> str | None:
        for record in self.experiences():
            if problem.lower() in record.metadata.get("problem", "").lower():
                return record.metadata.get("solution")
        return None
