"""
Short Term Memory - Short-term memory store
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import MemoryEntry, MemoryType


class ShortTermMemory:
    """Short-term memory with TTL"""

    def __init__(self, config):
        self.config = config
        self._store: Dict[str, MemoryEntry] = {}

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def store(self, entry: MemoryEntry) -> UUID:
        self._store[entry.key] = entry
        return entry.id

    async def retrieve(
        self, key: str, agent_id: Optional[UUID] = None, workflow_id: Optional[UUID] = None
    ) -> Optional[MemoryEntry]:
        entry = self._store.get(key)
        if entry and (entry.expires_at is None or entry.expires_at > datetime.utcnow()):
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
            return entry
        return None

    async def search(
        self, query: str, limit: int = 10, agent_id: Optional[UUID] = None, filters: Optional[Dict] = None
    ) -> List[MemoryEntry]:
        results = []
        for entry in self._store.values():
            if query.lower() in str(entry.value).lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    async def delete(self, entry_id: UUID) -> bool:
        for key, entry in list(self._store.items()):
            if entry.id == entry_id:
                del self._store[key]
                return True
        return False

    async def get_for_consolidation(self, agent_id: Optional[UUID] = None) -> List[MemoryEntry]:
        return list(self._store.values())

    async def get_episodic(self, agent_id: Optional[UUID] = None) -> List[MemoryEntry]:
        return [
            e for e in self._store.values()
            if e.type == MemoryType.EPISODIC
        ]

    async def get_stats(self) -> Dict:
        return {"entries": len(self._store)}

    async def clear_agent(self, agent_id: UUID) -> int:
        count = 0
        for key, entry in list(self._store.items()):
            if entry.agent_id == agent_id:
                del self._store[key]
                count += 1
        return count

    async def export_agent(self, agent_id: UUID) -> Dict:
        return {}