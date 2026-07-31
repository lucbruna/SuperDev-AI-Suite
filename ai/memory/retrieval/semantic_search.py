from __future__ import annotations

from typing import Any


class SemanticSearch:
    """Semantic search over memory entries using content-based similarity."""

    def __init__(self):
        self._search_count: int = 0

    @property
    def search_count(self) -> int:
        return self._search_count

    def search(self, query: str, entries: list[dict[str, Any]], top_k: int = 10) -> list[dict[str, Any]]:
        q_words = set(query.lower().split())
        scored: list[tuple] = []
        for entry in entries:
            content = str(entry.get("content", ""))
            entry_words = set(content.lower().split())
            if not q_words or not entry_words:
                score = 0.0
            else:
                score = len(q_words & entry_words) / max(len(q_words | entry_words), 1)
            scored.append((score, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        self._search_count += 1
        return [entry for _, entry in scored[:top_k]]

    def search_by_embedding(self, query: str, entries: list[dict[str, Any]], top_k: int = 10) -> list[dict[str, Any]]:
        q_words = set(query.lower().split())
        scored: list[tuple] = []
        for entry in entries:
            content = str(entry.get("content", ""))
            embedding = entry.get("embedding", [])
            if embedding and q_words:
                sim = self._embedding_similarity(q_words, embedding)
            else:
                entry_words = set(content.lower().split())
                sim = len(q_words & entry_words) / max(len(q_words | entry_words), 1)
            scored.append((sim, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        self._search_count += 1
        return [entry for _, entry in scored[:top_k]]

    def _embedding_similarity(self, query_words: set, embedding: Any) -> float:
        if isinstance(embedding, list) and len(embedding) > 0:
            return sum(embedding[: min(len(embedding), 10)]) / max(len(embedding), 1)
        return 0.0

    def reset(self) -> None:
        self._search_count = 0
