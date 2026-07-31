from __future__ import annotations

import logging

from ..knowledge_models import SearchResult


class Reranker:
    """Re-scores search results by blending base score with query overlap."""

    def __init__(self, keyword_bonus: float = 0.1) -> None:
        self._log = logging.getLogger("superdev.knowledge.rag.reranker")
        self._keyword_bonus = keyword_bonus

    def rerank(self, query: str, results: list[SearchResult], top_k: int = 0) -> list[SearchResult]:
        query_tokens = set(query.lower().split())
        reranked: list[SearchResult] = []
        for result in results:
            score = result.score
            if query_tokens:
                text_tokens = set(result.text.lower().split())
                overlap = len(query_tokens & text_tokens)
                score += (overlap / len(query_tokens)) * self._keyword_bonus
            reranked.append(
                SearchResult(
                    text=result.text,
                    score=score,
                    source=result.source,
                    document_id=result.document_id,
                    metadata=dict(result.metadata),
                )
            )
        reranked.sort(key=lambda result: result.score, reverse=True)
        if top_k > 0:
            reranked = reranked[:top_k]
        return reranked
