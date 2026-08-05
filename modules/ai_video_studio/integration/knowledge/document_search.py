"""Document Search — keyword retrieval over indexed documents."""
from __future__ import annotations

import re
from typing import Any


class DocumentSearch:
    """Stores documents and retrieves by keyword overlap."""

    def __init__(self) -> None:
        self._docs: list[dict[str, Any]] = []

    def index(self, text: str, *, id: str | None = None, **meta: Any) -> dict[str, Any]:
        doc = {"id": id or f"doc_{len(self._docs) + 1}", "text": text, **meta}
        self._docs = [d for d in self._docs if d["id"] != doc["id"]]
        self._docs.append(doc)
        return {"indexed": len(self._docs), "id": doc["id"]}

    def search(self, query: str, *, top_k: int = 5) -> dict[str, Any]:
        terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) > 2]
        results: list[dict[str, Any]] = []
        for doc in self._docs:
            text = doc["text"].lower()
            score = sum(1 for t in terms if t in text)
            if score:
                results.append({"id": doc["id"], "text": doc["text"], "score": score})
        results.sort(key=lambda r: -r["score"])
        return {"query": query, "results": results[:top_k], "count": len(results[:top_k])}

    def stats(self) -> dict[str, Any]:
        return {"indexed": len(self._docs)}


_document_search: DocumentSearch | None = None


def get_document_search() -> DocumentSearch:
    global _document_search
    if _document_search is None:
        _document_search = DocumentSearch()
    return _document_search
