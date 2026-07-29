"""
Memory Manager - Enterprise memory system for AI agents
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from enterprise_ai_core.models import (
    MemoryEntry,
    MemoryType,
    Event,
    EventType,
)
from enterprise_ai_core.memory.short_memory import ShortTermMemory
from enterprise_ai_core.memory.long_memory import LongTermMemory
from enterprise_ai_core.memory.vector_memory import VectorMemory
from enterprise_ai_core.memory.knowledge_store import KnowledgeStore


class MemoryManager:
    """Manages multi-tier memory system for enterprise AI"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config
        self.short_term = ShortTermMemory(self.config.memory)
        self.long_term = LongTermMemory(self.config.memory)
        self.vector_memory = VectorMemory(self.config.memory)
        self.knowledge_store = KnowledgeStore(self.config.memory)
        self._initialized = False

    async def initialize(self) -> None:
        await self.short_term.initialize()
        await self.long_term.initialize()
        await self.vector_memory.initialize()
        await self.knowledge_store.initialize()
        self._initialized = True

    async def shutdown(self) -> None:
        await self.short_term.shutdown()
        await self.long_term.shutdown()
        await self.vector_memory.shutdown()
        await self.knowledge_store.shutdown()

    async def store(self, entry: MemoryEntry) -> UUID:
        if entry.type == MemoryType.SHORT_TERM:
            return await self.short_term.store(entry)
        elif entry.type == MemoryType.LONG_TERM:
            return await self.long_term.store(entry)
        elif entry.type == MemoryType.VECTOR:
            return await self.vector_memory.store(entry)
        elif entry.type == MemoryType.KNOWLEDGE:
            return await self.knowledge_store.store(entry)
        elif entry.type == MemoryType.EPISODIC:
            return await self.short_term.store(entry)
        elif entry.type == MemoryType.SEMANTIC:
            return await self.vector_memory.store(entry)

        return await self.short_term.store(entry)

    async def retrieve(
        self,
        key: str,
        memory_type: Optional[MemoryType] = None,
        agent_id: Optional[UUID] = None,
        workflow_id: Optional[UUID] = None,
    ) -> Optional[MemoryEntry]:
        if memory_type == MemoryType.SHORT_TERM or memory_type is None:
            result = await self.short_term.retrieve(key, agent_id, workflow_id)
            if result:
                return result

        if memory_type == MemoryType.LONG_TERM or memory_type is None:
            result = await self.long_term.retrieve(key, agent_id, workflow_id)
            if result:
                return result

        if memory_type == MemoryType.VECTOR or memory_type is None:
            result = await self.vector_memory.retrieve(key, agent_id, workflow_id)
            if result:
                return result

        if memory_type == MemoryType.KNOWLEDGE:
            return await self.knowledge_store.retrieve(key)

        return None

    async def search(
        self,
        query: str,
        memory_type: MemoryType = MemoryType.VECTOR,
        limit: int = 10,
        agent_id: Optional[UUID] = None,
        filters: Optional[Dict] = None,
    ) -> List[MemoryEntry]:
        if memory_type == MemoryType.VECTOR:
            return await self.vector_memory.search(query, limit, agent_id, filters)
        elif memory_type == MemoryType.KNOWLEDGE:
            return await self.knowledge_store.search(query, limit, filters)
        elif memory_type == MemoryType.LONG_TERM:
            return await self.long_term.search(query, limit, agent_id, filters)
        else:
            return await self.short_term.search(query, limit, agent_id, filters)

    async def delete(self, entry_id: UUID, memory_type: MemoryType) -> bool:
        if memory_type == MemoryType.SHORT_TERM:
            return await self.short_term.delete(entry_id)
        elif memory_type == MemoryType.LONG_TERM:
            return await self.long_term.delete(entry_id)
        elif memory_type == MemoryType.VECTOR:
            return await self.vector_memory.delete(entry_id)
        elif memory_type == MemoryType.KNOWLEDGE:
            return await self.knowledge_store.delete(entry_id)
        return False

    async def consolidate(self, agent_id: Optional[UUID] = None) -> Dict[str, int]:
        results = {"short_to_long": 0, "episodic_to_semantic": 0}

        short_entries = await self.short_term.get_for_consolidation(agent_id)
        for entry in short_entries:
            if entry.access_count > 3 or entry.importance > 0.7:
                entry.type = MemoryType.LONG_TERM
                await self.long_term.store(entry)
                await self.short_term.delete(entry.id)
                results["short_to_long"] += 1

        episodic_entries = await self.short_term.get_episodic(agent_id)
        for entry in episodic_entries:
            if entry.created_at < datetime.utcnow() - timedelta(days=30):
                entry.type = MemoryType.SEMANTIC
                await self.vector_memory.store(entry)
                await self.short_term.delete(entry.id)
                results["episodic_to_semantic"] += 1

        return results

    async def get_stats(self) -> Dict[str, Any]:
        return {
            "short_term": await self.short_term.get_stats(),
            "long_term": await self.long_term.get_stats(),
            "vector": await self.vector_memory.get_stats(),
            "knowledge": await self.knowledge_store.get_stats(),
        }

    async def clear_agent_memory(self, agent_id: UUID) -> int:
        count = 0
        count += await self.short_term.clear_agent(agent_id)
        count += await self.long_term.clear_agent(agent_id)
        count += await self.vector_memory.clear_agent(agent_id)
        return count

    async def export_memory(self, agent_id: UUID) -> Dict[str, Any]:
        return {
            "short_term": await self.short_term.export_agent(agent_id),
            "long_term": await self.long_term.export_agent(agent_id),
            "vector": await self.vector_memory.export_agent(agent_id),
            "knowledge": await self.knowledge_store.export_agent(agent_id),
        }