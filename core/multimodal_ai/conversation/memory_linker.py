from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class Memory:
    key: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    access_count: int = 0


class MemoryLinker:
    def __init__(self) -> None:
        self._memories: dict[str, Memory] = {}
        self._links: dict[str, list[str]] = {}

    def store_memory(self, key: str, content: str, metadata: Optional[dict[str, Any]] = None) -> str:
        memory = Memory(
            key=key,
            content=content,
            metadata=metadata or {},
            created_at=datetime.now().isoformat(),
        )
        self._memories[key] = memory
        return key

    def retrieve_memory(self, query: str) -> list[dict[str, Any]]:
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        for key, mem in self._memories.items():
            content_lower = mem.content.lower()
            score = 0
            for word in query_words:
                if word in content_lower:
                    score += 1
            if score > 0:
                results.append(
                    {
                        "key": key,
                        "content": mem.content,
                        "metadata": mem.metadata,
                        "score": score,
                        "created_at": mem.created_at,
                    }
                )
                mem.access_count += 1
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def link_memories(self, source_key: str, target_key: str) -> bool:
        if source_key not in self._memories or target_key not in self._memories:
            return False
        if source_key not in self._links:
            self._links[source_key] = []
        if target_key not in self._links[source_key]:
            self._links[source_key].append(target_key)
        return True

    def search_memories(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        results = self.retrieve_memory(query)
        return results[:limit]

    def get_relevant_history(self, query: str, max_results: int = 5) -> list[dict[str, Any]]:
        results = self.retrieve_memory(query)
        return [
            r for r in results
            if "conversation_id" in r["metadata"]
        ][:max_results]

    def forget_memory(self, key: str) -> bool:
        if key in self._memories:
            del self._memories[key]
            self._links.pop(key, None)
            for linked in self._links.values():
                if key in linked:
                    linked.remove(key)
            return True
        return False
