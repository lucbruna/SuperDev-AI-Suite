from __future__ import annotations

import logging
from typing import Any

from ..knowledge_config import KnowledgeConfig
from ..knowledge_events import KnowledgeEvents, KnowledgeEventType
from ..knowledge_interfaces import MemoryStore
from ..knowledge_metrics import KnowledgeMetrics
from ..knowledge_models import MemoryRecord
from .episodic_memory import EpisodicMemory
from .long_term_memory import LongTermMemory
from .memory_cleanup import MemoryCleanup
from .memory_optimizer import MemoryOptimizer
from .memory_storage import InMemoryMemoryStorage
from .procedural_memory import ProceduralMemory
from .semantic_memory import SemanticMemory
from .short_term_memory import ShortTermMemory
from .working_memory import WorkingMemory


class MemoryEngine:
    """Composes all memory types into a single subsystem."""

    def __init__(
        self,
        store: MemoryStore | None = None,
        config: KnowledgeConfig | None = None,
        events: KnowledgeEvents | None = None,
        metrics: KnowledgeMetrics | None = None,
    ) -> None:
        self._log = logging.getLogger("superdev.knowledge.memory.engine")
        self.config = config or KnowledgeConfig()
        self.events = events or KnowledgeEvents()
        self.metrics = metrics or KnowledgeMetrics()
        self.backend = store or InMemoryMemoryStorage(self.config.memory_limit)
        self.short_term = ShortTermMemory(self.config.short_term_limit)
        self.long_term = LongTermMemory(self.backend)
        self.episodic = EpisodicMemory(self.backend)
        self.semantic = SemanticMemory(self.backend)
        self.procedural = ProceduralMemory(self.backend)
        self.working = WorkingMemory()
        self.cleanup = MemoryCleanup(self.backend)
        self.optimizer = MemoryOptimizer(self.backend)

    def store(self, content: str, memory_type: str = "episodic", importance: float = 0.5,
              metadata: dict[str, Any] | None = None) -> str:
        record = MemoryRecord(
            content=content, memory_type=memory_type, importance=importance, metadata=metadata or {},
        )
        record_id = self.backend.save(record)
        self.metrics.increment("memory.engine.stored")
        self.events.emit(KnowledgeEventType.MEMORY_STORED, {"record_id": record_id, "type": memory_type})
        return record_id

    def recall(self, memory_type: str | None = None) -> list[MemoryRecord]:
        records = self.backend.list(memory_type)
        self.metrics.increment("memory.engine.recalled")
        return records

    def prune(self) -> int:
        removed = self.cleanup.prune_expired(self.config.retention_days)
        removed += self.cleanup.prune_low_importance()
        removed += self.cleanup.prune_to_capacity(self.config.memory_limit)
        self.events.emit(KnowledgeEventType.MEMORY_PRUNED, {"removed": removed})
        return removed

    def optimize(self) -> dict[str, int]:
        return {
            "deduplicated": self.optimizer.deduplicate(),
            "consolidated": self.optimizer.consolidate_similar(),
            "reweighted": self.optimizer.reweight(),
        }

    def stats(self) -> dict[str, Any]:
        return {
            "records": self.backend.count(),
            "short_term": self.short_term.size(),
            "working_task": self.working.current_task(),
        }
