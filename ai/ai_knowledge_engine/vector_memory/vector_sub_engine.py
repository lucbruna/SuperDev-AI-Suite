"""Vector memory subsystem engine — Vector-based memory for similarity search."""
import uuid
import math
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class VectorEntry:
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    text: str = ""
    vector: List[float] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class VectorSubEngine:
    def __init__(self, dimensions: int = 128):
        self._entries: Dict[str, VectorEntry] = {}
        self._dimensions = dimensions
        self._index: Dict[str, List[str]] = {}

    def store(self, text: str, vector: Optional[List[float]] = None, metadata: Optional[Dict[str, Any]] = None) -> VectorEntry:
        if vector is None:
            vector = self._hash_embed(text)
        entry = VectorEntry(text=text, vector=vector, metadata=metadata or {})
        self._entries[entry.entry_id] = entry
        return entry

    def get(self, entry_id: str) -> Optional[VectorEntry]:
        return self._entries.get(entry_id)

    def delete(self, entry_id: str) -> bool:
        return self._entries.pop(entry_id, None) is not None

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_vector = self._hash_embed(query)
        scored = []
        for entry in self._entries.values():
            score = self._cosine_similarity(query_vector, entry.vector)
            scored.append({"entry": entry, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return [
            {"id": s["entry"].entry_id, "text": s["entry"].text, "score": s["score"], "metadata": s["entry"].metadata}
            for s in scored[:top_k]
        ]

    def search_by_vector(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        scored = []
        for entry in self._entries.values():
            score = self._cosine_similarity(vector, entry.vector)
            scored.append({"entry": entry, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return [
            {"id": s["entry"].entry_id, "text": s["entry"].text, "score": s["score"]}
            for s in scored[:top_k]
        ]

    def get_similar(self, entry_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        entry = self._entries.get(entry_id)
        if not entry:
            return []
        results = []
        for other in self._entries.values():
            if other.entry_id != entry_id:
                score = self._cosine_similarity(entry.vector, other.vector)
                results.append({"id": other.entry_id, "text": other.text, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def optimize(self) -> int:
        removed = 0
        to_remove = []
        entries = list(self._entries.values())
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                score = self._cosine_similarity(entries[i].vector, entries[j].vector)
                if score > 0.99:
                    to_remove.append(entries[j].entry_id)
        for rid in set(to_remove):
            self._entries.pop(rid, None)
            removed += 1
        return removed

    def _hash_embed(self, text: str) -> List[float]:
        import hashlib
        h = hashlib.sha256(text.encode()).hexdigest()
        vector = []
        for i in range(0, min(len(h), self._dimensions * 2), 2):
            val = int(h[i:i+2], 16) / 255.0
            vector.append(val)
        while len(vector) < self._dimensions:
            vector.append(0.0)
        return vector[:self._dimensions]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if len(a) != len(b) or not a:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def get_stats(self) -> dict:
        return {
            "total_entries": len(self._entries),
            "dimensions": self._dimensions,
        }
