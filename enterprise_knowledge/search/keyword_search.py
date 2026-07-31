"""Keyword search over text and records."""

from __future__ import annotations

from typing import Any

from enterprise_knowledge.knowledge_protocols import tokenize


class KeywordSearch:
    """Scoring of documents/records by term overlap (BM25-style)."""

    def __init__(self, stopwords: set[str] | None = None) -> None:
        self.stopwords = stopwords or {
            "de", "da", "do", "e", "o", "a", "os", "as", "um", "uma",
            "em", "com", "para", "por", "que", "ao", "no", "na", "o",
        }

    def score(self, query: str, text: str) -> float:
        query_terms = [t for t in tokenize(query) if t not in self.stopwords]
        if not query_terms:
            return 0.0
        text_terms = tokenize(text)
        if not text_terms:
            return 0.0
        counts: dict[str, int] = {}
        for term in text_terms:
            counts[term] = counts.get(term, 0) + 1
        hits = sum(counts.get(term, 0) for term in query_terms)
        return hits / len(text_terms)

    def search(self, query: str, records: list[dict[str, Any]],
               text_field: str = "text",
               limit: int = 10) -> list[dict[str, Any]]:
        scored = []
        for record in records:
            text = record.get(text_field, "") or ""
            score = self.score(query, text)
            if score <= 0:
                continue
            item = dict(record)
            item["score"] = score
            scored.append(item)
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:max(0, limit)]
