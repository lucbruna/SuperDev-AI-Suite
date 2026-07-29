"""
Long Term Memory - Long-term persistent memory store
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import MemoryEntry, MemoryType


class LongTermMemory:
    """Long-term persistent memory"""

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
        return self._store.get(key)

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

    async def get_stats(self) -> Dict:
        return {"entries": len(self._store)}

    async def clear_agent(self, agent_id: UUID) -> int:
        return 0

    async def export_agent(self, agent_id: UUID) -> Dict:
        return {}