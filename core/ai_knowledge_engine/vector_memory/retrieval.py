from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class RetrievedDocument:
    id: str
    vector: list[float]
    metadata: dict[str, Any]
    score: Optional[float] = None


class RetrievalEngine:
    def __init__(self) -> None:
        self._documents: dict[str, list[float]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def retrieve(self, query_vector: list[float], top_k: int = 10) -> list[RetrievedDocument]:
        scored: list[tuple[str, float]] = []
        for doc_id, vec in self._documents.items():
            score = self._cosine_similarity(query_vector, vec)
            scored.append((doc_id, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            RetrievedDocument(id=doc_id, vector=self._documents[doc_id], metadata=self._metadata.get(doc_id, {}), score=score)
            for doc_id, score in scored[:top_k]
        ]

    def retrieve_by_id(self, doc_id: str) -> Optional[RetrievedDocument]:
        if doc_id not in self._documents:
            return None
        return RetrievedDocument(
            id=doc_id,
            vector=self._documents[doc_id],
            metadata=self._metadata.get(doc_id, {}),
        )

    def batch_retrieve(self, doc_ids: list[str]) -> list[RetrievedDocument]:
        result: list[RetrievedDocument] = []
        for doc_id in doc_ids:
            doc = self.retrieve_by_id(doc_id)
            if doc:
                result.append(doc)
        return result

    def retrieve_by_metadata(self, filters: dict[str, Any]) -> list[RetrievedDocument]:
        result: list[RetrievedDocument] = []
        for doc_id, meta in self._metadata.items():
            match = True
            for key, value in filters.items():
                if meta.get(key) != value:
                    match = False
                    break
            if match:
                result.append(RetrievedDocument(
                    id=doc_id,
                    vector=self._documents[doc_id],
                    metadata=meta,
                ))
        return result

    def retrieve_similar(self, doc_id: str, top_k: int = 10) -> list[RetrievedDocument]:
        if doc_id not in self._documents:
            return []
        query_vec = self._documents[doc_id]
        scored: list[tuple[str, float]] = []
        for vid, vec in self._documents.items():
            if vid == doc_id:
                continue
            score = self._cosine_similarity(query_vec, vec)
            scored.append((vid, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            RetrievedDocument(id=did, vector=self._documents[did], metadata=self._metadata.get(did, {}), score=score)
            for did, score in scored[:top_k]
        ]

    def add_document(self, doc_id: str, vector: list[float], metadata: Optional[dict[str, Any]] = None) -> None:
        self._documents[doc_id] = vector
        self._metadata[doc_id] = metadata or {}

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(ai * bi for ai, bi in zip(a, b))
        na = math.sqrt(sum(ai * ai for ai in a))
        nb = math.sqrt(sum(bi * bi for bi in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)
