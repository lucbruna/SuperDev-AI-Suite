"""Semantic cache."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.9) -> None:
        self._entries: List[Dict[str, Any]] = []
        self._threshold = similarity_threshold
    def _similarity(self, a: str, b: str) -> float:
        a_words = set(a.lower().split())
        b_words = set(b.lower().split())
        if not a_words or not b_words:
            return 0.0
        intersection = a_words & b_words
        union = a_words | b_words
        return len(intersection) / len(union) if union else 0.0
    def get(self, query: str) -> Optional[Dict[str, Any]]:
        best_match = None
        best_score = 0
        for entry in self._entries:
            score = self._similarity(query, entry["query"])
            if score >= self._threshold and score > best_score:
                best_score = score
                best_match = entry
        if best_match:
            best_match["access_count"] += 1
            return best_match["value"]
        return None
    def set(self, query: str, value: Any, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        entry = {"query": query, "value": value, "metadata": metadata or {}, "created_at": time.time(), "access_count": 0}
        self._entries.append(entry)
        return {"query": query, "cached": True}
    def invalidate(self, query: str = "") -> int:
        if not query:
            n = len(self._entries)
            self._entries.clear()
            return n
        original = len(self._entries)
        self._entries = [e for e in self._entries if self._similarity(query, e["query"]) < self._threshold]
        return original - len(self._entries)
    def find_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        scored = [{"query": e["query"], "similarity": self._similarity(query, e["query"])} for e in self._entries]
        return sorted(scored, key=lambda x: x["similarity"], reverse=True)[:top_k]
    def count(self) -> int:
        return len(self._entries)
    def clear(self) -> int:
        n = len(self._entries)
        self._entries.clear()
        return n
