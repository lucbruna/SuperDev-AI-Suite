from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents
from ..knowledge_interfaces import MemoryStore
from ..knowledge_metrics import KnowledgeMetrics
from .episodic_memory import EpisodicMemory
from .long_term_memory import LongTermMemory
from .memory_storage import FileMemoryStorage, InMemoryMemoryStorage
from .procedural_memory import ProceduralMemory
from .semantic_memory import SemanticMemory
from .short_term_memory import ShortTermMemory
from .working_memory import WorkingMemory


class MemoryManager:
    """High-level facade over the memory subsystem for agents."""

    def __init__(
        self,
        store: MemoryStore | None = None,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.manager")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        backend = self.config.extra.get("memory_backend", "in-memory")
        self.store = store or (
            FileMemoryStorage(self.config.storage_path + "/memory.json") if backend == "file" else InMemoryMemoryStorage()
        )
        self.short_term = ShortTermMemory(self.config.short_term_limit)
        self.long_term = LongTermMemory(self.store)
        self.episodic = EpisodicMemory(self.store)
        self.semantic = SemanticMemory(self.store)
        self.procedural = ProceduralMemory(self.store)
        self.working = WorkingMemory()

    def remember_current_task(self, key: str, value: str) -> None:
        self.short_term.remember(key, value)

    def context_snapshot(self) -> dict[str, Any]:
        return {
            "short_term": self.short_term.snapshot(),
            "working_task": self.working.current_task(),
            "working_slots": self.working.snapshot(),
        }

    def commit_long_term(self, content: str, importance: float = 0.5, metadata: dict[str, Any] | None = None) -> str:
        return self.long_term.commit(content, importance, metadata)

    def log_experience(self, problem: str, solution: str, outcome: str = "success") -> str:
        return self.episodic.record_experience(problem, solution, outcome)

    def store_procedure(self, name: str, steps: list[str]) -> str:
        return self.procedural.store_procedure(name, steps)

    def store_fact(self, fact: str, subject: str = "") -> str:
        return self.semantic.store_fact(fact, subject)

    def recall_all(self) -> dict[str, list[Any]]:
        return {
            "long_term": self.long_term.recall(),
            "episodic": self.episodic.experiences(),
            "semantic": self.semantic.facts(),
            "procedural": self.procedural.procedures(),
        }

    def status(self) -> dict[str, Any]:
        return {
            "store_records": self.store.count(),
            "short_term_entries": self.short_term.size(),
            "procedures": len(self.procedural.procedures()),
        }
