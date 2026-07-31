"""Full-text search engine with in-memory index and query support."""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


class SearchableType(StrEnum):
    DOCUMENT = "document"
    USER = "user"
    PROJECT = "project"
    KNOWLEDGE = "knowledge"
    PLUGIN = "plugin"
    CUSTOM = "custom"


@dataclass
class SearchDocument:
    id: str
    type: SearchableType
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SearchResult:
    document_id: str
    document_type: str
    title: str
    snippet: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class FullTextSearch:
    """In-memory full-text search engine with TF-IDF-like scoring."""

    def __init__(self):
        self._documents: dict[str, SearchDocument] = {}
        self._index: dict[str, set[str]] = defaultdict(set)  # term -> doc_ids
        self._doc_lengths: dict[str, int] = {}
        self._stop_words: set[str] = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "need", "dare", "ought",
            "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "above", "below",
            "between", "out", "off", "over", "under", "again", "further", "then",
            "once", "and", "but", "or", "nor", "not", "so", "yet", "both",
            "either", "neither", "each", "every", "all", "any", "few", "more",
            "most", "other", "some", "such", "no", "only", "own", "same",
            "than", "too", "very", "just", "because", "if", "when", "while",
        }

    def _tokenize(self, text: str) -> list[str]:
        text = text.lower()
        text = re.sub(r"[^\w\s]", " ", text)
        tokens = text.split()
        return [t for t in tokens if t not in self._stop_words and len(t) > 1]

    def _build_doc_vector(self, tokens: list[str]) -> dict[str, int]:
        tf: dict[str, int] = defaultdict(int)
        for token in tokens:
            tf[token] += 1
        return dict(tf)

    def add_document(self, document: SearchDocument) -> None:
        self._documents[document.id] = document
        text = f"{document.title} {document.content}"
        tokens = self._tokenize(text)
        self._doc_lengths[document.id] = len(tokens)

        unique_tokens = set(tokens)
        for token in unique_tokens:
            self._index[token].add(document.id)

    def remove_document(self, doc_id: str) -> bool:
        if doc_id not in self._documents:
            return False

        document = self._documents[doc_id]
        text = f"{document.title} {document.content}"
        tokens = set(self._tokenize(text))

        for token in tokens:
            self._index[token].discard(doc_id)
            if not self._index[token]:
                del self._index[token]

        del self._documents[doc_id]
        self._doc_lengths.pop(doc_id, None)
        return True

    def search(
        self,
        query: str,
        doc_type: SearchableType | None = None,
        limit: int = 10,
        offset: int = 0,
    ) -> list[SearchResult]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        # Find candidate documents (union of all query term postings)
        candidate_ids: set[str] = set()
        for token in query_tokens:
            candidate_ids |= self._index.get(token, set())

        if not candidate_ids:
            return []

        # Score each candidate
        total_docs = len(self._documents)
        scores: list[tuple[str, float]] = []

        for doc_id in candidate_ids:
            document = self._documents[doc_id]
            if doc_type and document.type != doc_type:
                continue

            doc_text = f"{document.title} {document.content}"
            doc_tokens = self._tokenize(doc_text)
            doc_tf = self._build_doc_vector(doc_tokens)
            doc_len = len(doc_tokens) or 1

            score = 0.0
            for token in query_tokens:
                tf = doc_tf.get(token, 0) / doc_len
                df = len(self._index.get(token, set()))
                idf = (total_docs / (1 + df)) if df > 0 else 0
                score += tf * idf

            # Title boost
            if any(t in document.title.lower() for t in query_tokens):
                score *= 1.5

            scores.append((doc_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        results = []

        for doc_id, score in scores[offset: offset + limit]:
            document = self._documents[doc_id]
            snippet = self._generate_snippet(document.content, query_tokens)
            results.append(
                SearchResult(
                    document_id=doc_id,
                    document_type=document.type.value,
                    title=document.title,
                    snippet=snippet,
                    score=round(score, 4),
                    metadata=document.metadata,
                )
            )

        return results

    def _generate_snippet(self, content: str, query_tokens: list[str], max_length: int = 200) -> str:
        words = content.split()
        if not words:
            return content[:max_length]

        best_start = 0
        best_score = 0
        for i in range(len(words)):
            window = words[i: i + 10]
            score = sum(1 for w in window if w.lower() in query_tokens)
            if score > best_score:
                best_score = score
                best_start = i

        snippet_words = words[max(0, best_start - 5): best_start + 15]
        snippet = " ".join(snippet_words)
        if len(snippet) > max_length:
            snippet = snippet[:max_length] + "..."
        return snippet

    def update_document(self, doc_id: str, **kwargs: Any) -> bool:
        doc = self._documents.get(doc_id)
        if not doc:
            return False

        self.remove_document(doc_id)

        for key, value in kwargs.items():
            if hasattr(doc, key):
                setattr(doc, key, value)
        doc.updated_at = datetime.now(UTC)

        self.add_document(doc)
        return True

    def get_document(self, doc_id: str) -> SearchDocument | None:
        return self._documents.get(doc_id)

    def list_documents(
        self,
        doc_type: SearchableType | None = None,
        limit: int = 50,
    ) -> list[SearchDocument]:
        docs = list(self._documents.values())
        if doc_type:
            docs = [d for d in docs if d.type == doc_type]
        return sorted(docs, key=lambda d: d.updated_at, reverse=True)[:limit]

    def get_stats(self) -> dict[str, Any]:
        return {
            "total_documents": len(self._documents),
            "total_terms": len(self._index),
            "by_type": {
                dt.value: sum(1 for d in self._documents.values() if d.type == dt)
                for dt in SearchableType
            },
            "avg_doc_length": (
                sum(self._doc_lengths.values()) / len(self._doc_lengths)
                if self._doc_lengths else 0
            ),
        }


full_text_search = FullTextSearch()
