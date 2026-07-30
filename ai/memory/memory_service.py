from __future__ import annotations

from typing import Any, Dict, List, Optional

from .memory_manager import MemoryManager
from .memory_models import MemoryEntry, MemoryQuery, MemorySummary
from .memory_types import MemoryCategory, MemoryData, MemoryID, MemoryScope, Tags


class MemoryService:
    """High-level service facade for external memory consumers."""

    def __init__(self, manager: MemoryManager):
        self._manager = manager

    @property
    def manager(self) -> MemoryManager:
        return self._manager

    async def remember(
        self,
        key: MemoryID,
        data: MemoryData,
        tags: Tags | None = None,
        ttl: float | None = None,
        user: str = "",
    ) -> bool:
        return await self._manager.store(key, data, tags=tags, ttl=ttl, user=user)

    async def recall(self, key: MemoryID, user: str = "") -> MemoryData | None:
        return await self._manager.retrieve(key, user=user)

    async def forget(self, key: MemoryID, user: str = "") -> bool:
        return await self._manager.delete(key, user=user)

    async def update_memory(self, key: MemoryID, data: MemoryData, user: str = "") -> bool:
        return await self._manager.update(key, data, user=user)

    async def find(self, query: str, user: str = "") -> List[MemoryEntry]:
        q = MemoryQuery(query=query)
        return await self._manager.search(q, user=user)

    async def find_by_tags(self, tags: Tags, user: str = "") -> List[MemoryEntry]:
        q = MemoryQuery(tags=tags)
        return await self._manager.search(q, user=user)

    async def get_context(self, context_id: str, limit: int = 50) -> List[MemoryEntry]:
        from .memory_context import MemoryContext
        ctx = MemoryContext(context_id, max_length=limit)
        q = MemoryQuery(scope=MemoryScope.SESSION, max_results=limit)
        entries = await self._manager.search(q)
        for e in entries:
            ctx.add_entry(e)
        return ctx.entries

    async def get_summary(self) -> MemorySummary:
        return await self._manager.get_stats()

    async def run_maintenance(self) -> Dict[str, Any]:
        expired = await self._manager.evict_expired()
        consolidated = await self._manager.consolidate()
        stats = await self._manager.get_stats()
        return {
            "expired_evicted": expired,
            "consolidated": consolidated,
            "total_entries": stats.total_entries,
            "total_size_bytes": stats.total_size_bytes,
        }

    async def health_check(self) -> Dict[str, Any]:
        stats = await self._manager.get_stats()
        return {
            "healthy": self._manager.state.is_ready,
            "phase": self._manager.state.phase.name,
            "total_entries": stats.total_entries,
            "total_size_bytes": stats.total_size_bytes,
            "hit_rate": self._manager.metrics.hit_rate,
            "avg_latency": self._manager.metrics.avg_latency,
        }
