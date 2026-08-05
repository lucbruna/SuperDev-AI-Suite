"""AIOS Knowledge Memory — document store with keyword search.

Stores documents (title, content, tags); recall scores documents by
keyword overlap so knowledge is retrievable without a full-text engine.
"""

from __future__ import annotations

import re
import time
import uuid
from typing import Any

_WORD_RE = re.compile(r"[a-zA-Z0-9_]+")


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _WORD_RE.findall(str(text))}


class KnowledgeMemory:
    """Store of taggable knowledge documents."""

    def __init__(self, max_documents: int = 10_000) -> None:
        self._documents: list[dict[str, Any]] = []
        self._max = max_documents

    def store(self, content: Any, **meta: Any) -> dict[str, Any]:
        title = meta.get("title", "")
        document = {
            "record_id": f"knw-{uuid.uuid4().hex[:10]}",
            "title": title,
            "content": content,
            "tags": list(meta.get("tags", [])),
            "timestamp": time.time(),
        }
        self._documents.append(document)
        if len(self._documents) > self._max:
            self._documents = self._documents[-self._max:]
        return document

    def _score(self, document: dict[str, Any], query_tokens: set[str]) -> int:
        if not query_tokens:
            return 0
        text_tokens = _tokens(f"{document['title']} {document['content']}")
        return len(query_tokens & text_tokens)

    def recall(self, query: Any = None, limit: int = 5, **filters: Any) -> list[dict[str, Any]]:
        tags = set(filters.get("tags", []))
        query_tokens = _tokens(query) if query is not None else set()
        scored = []
        for document in self._documents:
            if tags and not tags.issubset(set(document["tags"])):
                continue
            score = self._score(document, query_tokens)
            if score or not query_tokens:
                scored.append((score, document))
        scored.sort(key=lambda pair: (-pair[0], pair[1]["timestamp"]))
        return [doc for _, doc in scored[:limit]]

    def forget(self, record_id: str) -> bool:
        before = len(self._documents)
        self._documents = [d for d in self._documents if d["record_id"] != record_id]
        return len(self._documents) < before

    def clear(self) -> None:
        self._documents.clear()

    def stats(self) -> dict[str, Any]:
        return {"documents": len(self._documents), "max": self._max}

    def snapshot(self) -> dict[str, Any]:
        return {"documents": len(self._documents), "max": self._max}
