from __future__ import annotations

from collections import Counter
from typing import Any
import re


class LexicalSearch:
    """Lexical (keyword-based) search using TF-IDF-like scoring."""

    def __init__(self):
        self._documents: dict[str, str] = {}

    def index(self, doc_id: str, text: str) -> None:
        self._documents[doc_id] = text

    def search(self, query: str, top_k: int = 10) -> list[dict[str, Any]]:
        query_terms = set(re.findall(r"\w+", query.lower()))
        results = []
        for doc_id, text in self._documents.items():
            doc_terms = Counter(re.findall(r"\w+", text.lower()))
            score = sum(doc_terms.get(term, 0) for term in query_terms)
            if score > 0:
                results.append({"id": doc_id, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
