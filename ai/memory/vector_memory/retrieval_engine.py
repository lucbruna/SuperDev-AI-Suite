from __future__ import annotations

from typing import Any

from .reranker import Reranker
from .vector_store import VectorStore


class RetrievalResult:
    """A single retrieval result with score and metadata."""

    def __init__(self, vector_id: str, score: float, metadata: dict[str, Any]):
        self._vector_id = vector_id
        self._score = score
        self._metadata = dict(metadata)

    @property
    def vector_id(self) -> str:
        return self._vector_id

    @property
    def score(self) -> float:
        return self._score

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def to_dict(self) -> dict[str, Any]:
        return {
            "vector_id": self._vector_id,
            "score": self._score,
            "metadata": dict(self._metadata),
        }


class RetrievalEngine:
    """High-level retrieval with optional reranking and filtering."""

    def __init__(self, store: VectorStore, reranker: Reranker | None = None):
        self._store = store
        self._reranker = reranker or Reranker()

    @property
    def store(self) -> VectorStore:
        return self._store

    def retrieve(
        self,
        query_vector: list[float],
        top_k: int = 10,
        metric: str = "cosine",
        metadata_filter: dict[str, Any] | None = None,
        rerank: bool = False,
    ) -> list[RetrievalResult]:
        raw = self._store.similarity_search(query_vector, top_k * 2 if rerank else top_k, metric)
        results: list[RetrievalResult] = []
        for vid, score in raw:
            meta = self._store.get_metadata(vid)
            if metadata_filter and not all(meta.get(k) == v for k, v in metadata_filter.items()):
                continue
            results.append(RetrievalResult(vid, score, meta))
        if rerank and results:
            results = self._reranker.rerank(query_vector, results)
        return results[:top_k]

    def retrieve_by_id(self, vector_id: str) -> RetrievalResult | None:
        vec = self._store.get(vector_id)
        if vec is None:
            return None
        meta = self._store.get_metadata(vector_id)
        return RetrievalResult(vector_id, 1.0, meta)
