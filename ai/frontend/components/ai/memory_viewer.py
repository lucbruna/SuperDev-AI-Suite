"""
AI Memory Viewer
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class MemoryType(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"


@dataclass
class MemoryEntry:
    id: str
    content: str
    memory_type: MemoryType
    importance: float = 0.5
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryViewer:
    def __init__(self):
        self.memories: List[MemoryEntry] = []
        self.filter_type: Optional[MemoryType] = None
        self.search_term: str = ""
        
    def add_memory(self, memory: MemoryEntry) -> None:
        self.memories.append(memory)
        
    def remove_memory(self, memory_id: str) -> bool:
        for i, m in enumerate(self.memories):
            if m.id == memory_id:
                self.memories.pop(i)
                return True
        return False
        
    def search(self, term: str) -> List[MemoryEntry]:
        return [m for m in self.memories if term.lower() in m.content.lower()]
        
    def get_by_type(self, memory_type: MemoryType) -> List[MemoryEntry]:
        return [m for m in self.memories if m.memory_type == memory_type]
        
    def get_important(self, min_importance: float = 0.7) -> List[MemoryEntry]:
        return [m for m in self.memories if m.importance >= min_importance]
        
    def render(self) -> Dict[str, Any]:
        return {
            "memories": [{"id": m.id, "type": m.memory_type.value, "importance": m.importance} for m in self.memories],
            "filterType": self.filter_type.value if self.filter_type else None,
        }
