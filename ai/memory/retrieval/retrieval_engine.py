from __future__ import annotations

from typing import Any, Dict, List, Optional

from .graph_search import GraphSearch
from .hybrid_search import HybridSearch
from .keyword_search import KeywordSearch
from .ranking import Ranking
from .relevance import Relevance
from .reranking import Reranking
from .scoring import Scoring
from .search import Search
from .semantic_search import SemanticSearch


class RetrievalEngine:
    """Facade for intelligent memory retrieval."""

    def __init__(self):
        self._search = Search()
        self._semantic = SemanticSearch()
        self._hybrid = HybridSearch()
        self._keyword = KeywordSearch()
        self._graph = GraphSearch()
        self._ranking = Ranking()
        self._reranking = Reranking()
        self._scoring = Scoring()
        self._relevance = Relevance()
        self._retrieval_count: int = 0

    @property
    def search(self) -> Search:
        return self._search

    @property
    def semantic(self) -> SemanticSearch:
        return self._semantic

    @property
    def hybrid(self) -> HybridSearch:
        return self._hybrid

    @property
    def keyword(self) -> KeywordSearch:
        return self._keyword

    @property
    def graph(self) -> GraphSearch:
        return self._graph

    @property
    def ranking(self) -> Ranking:
        return self._ranking

    @property
    def reranking(self) -> Reranking:
        return self._reranking

    @property
    def scoring(self) -> Scoring:
        return self._scoring

    @property
    def relevance(self) -> Relevance:
        return self._relevance

    def retrieve(self, query: str, entries: List[Dict[str, Any]], method: str = "search") -> List[Dict[str, Any]]:
        method_map = {
            "search": self._search.search,
            "semantic": self._semantic.search,
            "hybrid": self._hybrid.search,
            "keyword": self._keyword.search,
            "graph": self._graph.search,
        }
        fn = method_map.get(method, self._search.search)
        results = fn(query, entries)
        scored = self._scoring.score(query, results)
        ranked = self._ranking.rank(scored)
        self._retrieval_count += 1
        return ranked

    def snapshot(self) -> Dict[str, Any]:
        return {
            "retrieval_count": self._retrieval_count,
            "ranking_count": self._ranking.ranking_count,
            "reranking_count": self._reranking.reranking_count,
            "scoring_count": self._scoring.scoring_count,
        }
