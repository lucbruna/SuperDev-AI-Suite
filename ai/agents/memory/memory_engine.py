"""Central memory engine coordinating all memory subsystems."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .short_term import ShortTermMemory
from .long_term import LongTermMemory
from .episodic import EpisodicMemory
from .semantic import SemanticMemory
from .working_memory import WorkingMemory
from .vector_memory import VectorMemory
from .memory_search import MemorySearch
from .memory_cleanup import MemoryCleanup


class MemoryEngine:
    """Central memory engine coordinating all memory subsystems for agents."""

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None) -> None:
        self._agent_id = agent_id
        self._config = config or {}
        self._short_term = ShortTermMemory(
            max_size=self._config.get("short_term_size", 100),
        )
        self._long_term = LongTermMemory()
        self._episodic = EpisodicMemory()
        self._semantic = SemanticMemory()
        self._working = WorkingMemory()
        self._vector = VectorMemory()
        self._search = MemorySearch()
        self._cleanup = MemoryCleanup()
        self._total_store_count: int = 0
        self._total_retrieve_count: int = 0

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def short_term(self) -> ShortTermMemory:
        return self._short_term

    @property
    def long_term(self) -> LongTermMemory:
        return self._long_term

    @property
    def episodic(self) -> EpisodicMemory:
        return self._episodic

    @property
    def semantic(self) -> SemanticMemory:
        return self._semantic

    @property
    def working(self) -> WorkingMemory:
        return self._working

    @property
    def vector(self) -> VectorMemory:
        return self._vector

    def store(self, key: str, value: Any, memory_type: str = "short_term",
              metadata: Optional[Dict[str, Any]] = None) -> bool:
        entry = {
            "key": key,
            "value": value,
            "metadata": metadata or {},
            "timestamp": time.time(),
            "agent_id": self._agent_id,
        }
        if memory_type == "short_term":
            self._short_term.store(key, entry)
        elif memory_type == "long_term":
            self._long_term.store(key, entry)
        elif memory_type == "episodic":
            self._episodic.store(key, entry)
        elif memory_type == "semantic":
            self._semantic.store(key, entry)
        elif memory_type == "working":
            self._working.store(key, entry)
        elif memory_type == "vector":
            self._vector.store(key, entry)
        else:
            return False
        self._total_store_count += 1
        return True

    def retrieve(self, key: str, memory_type: str = "short_term") -> Optional[Any]:
        self._total_retrieve_count += 1
        if memory_type == "short_term":
            return self._short_term.retrieve(key)
        elif memory_type == "long_term":
            return self._long_term.retrieve(key)
        elif memory_type == "episodic":
            return self._episodic.retrieve(key)
        elif memory_type == "semantic":
            return self._semantic.retrieve(key)
        elif memory_type == "working":
            return self._working.retrieve(key)
        elif memory_type == "vector":
            return self._vector.retrieve(key)
        return None

    def recall(self, query: str, memory_type: Optional[str] = None,
               limit: int = 10) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        types = [memory_type] if memory_type else [
            "short_term", "long_term", "episodic", "semantic",
        ]
        for mt in types:
            found = self._search.search(self._get_memory_ref(mt), query, limit)
            results.extend(found)
        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:limit]

    def _get_memory_ref(self, memory_type: str) -> Any:
        mapping = {
            "short_term": self._short_term,
            "long_term": self._long_term,
            "episodic": self._episodic,
            "semantic": self._semantic,
            "working": self._working,
            "vector": self._vector,
        }
        return mapping.get(memory_type, self._short_term)

    def consolidate(self) -> Dict[str, Any]:
        promoted = 0
        for key, entry in self._short_term.get_all().items():
            if entry.get("metadata", {}).get("importance", 0) > 0.7:
                self._long_term.store(key, entry)
                promoted += 1
        return {"promoted_to_long_term": promoted}

    def cleanup(self, max_age_hours: int = 168) -> Dict[str, Any]:
        return self._cleanup.cleanup_all(self, max_age_hours)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "agent_id": self._agent_id,
            "short_term_count": self._short_term.count(),
            "long_term_count": self._long_term.count(),
            "episodic_count": self._episodic.count(),
            "semantic_count": self._semantic.count(),
            "working_count": self._working.count(),
            "vector_count": self._vector.count(),
            "total_stores": self._total_store_count,
            "total_retrieves": self._total_retrieve_count,
        }
