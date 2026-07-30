from __future__ import annotations

from ..retrieval_engine import RetrievalEngine
from ..search import Search
from ..semantic_search import SemanticSearch
from ..hybrid_search import HybridSearch
from ..keyword_search import KeywordSearch
from ..graph_search import GraphSearch
from ..ranking import Ranking
from ..reranking import Reranking
from ..scoring import Scoring
from ..relevance import Relevance


class TestRetrievalEngine:
    def setup_method(self) -> None:
        self.engine = RetrievalEngine()

    def test_retrieve(self) -> None:
        entries = [{"content": "hello world"}, {"content": "goodbye"}]
        results = self.engine.retrieve("hello", entries)
        assert len(results) >= 1

    def test_retrieve_with_method(self) -> None:
        entries = [{"content": "hello world"}, {"content": "goodbye"}]
        results = self.engine.retrieve("goodbye", entries, method="keyword")
        assert len(results) >= 1

    def test_snapshot(self) -> None:
        snap = self.engine.snapshot()
        assert "retrieval_count" in snap

    def test_properties(self) -> None:
        assert isinstance(self.engine.search, Search)
        assert isinstance(self.engine.semantic, SemanticSearch)
        assert isinstance(self.engine.hybrid, HybridSearch)
        assert isinstance(self.engine.keyword, KeywordSearch)
        assert isinstance(self.engine.graph, GraphSearch)
        assert isinstance(self.engine.ranking, Ranking)
        assert isinstance(self.engine.reranking, Reranking)
        assert isinstance(self.engine.scoring, Scoring)
        assert isinstance(self.engine.relevance, Relevance)


class TestSearch:
    def setup_method(self) -> None:
        self.search = Search()

    def test_search(self) -> None:
        entries = [{"content": "hello world"}, {"content": "goodbye world"}]
        results = self.search.search("world", entries)
        assert len(results) == 2

    def test_search_no_match(self) -> None:
        results = self.search.search("xyz", [{"content": "hello"}])
        assert len(results) == 0

    def test_search_fields(self) -> None:
        entries = [{"title": "hello", "content": "world"}, {"title": "foo", "content": "bar"}]
        results = self.search.search_fields("hello", entries, ["title"])
        assert len(results) == 1

    def test_reset(self) -> None:
        self.search.search("x", [{"content": "x"}])
        self.search.reset()
        assert self.search.search_count == 0


class TestSemanticSearch:
    def setup_method(self) -> None:
        self.semantic = SemanticSearch()

    def test_search(self) -> None:
        entries = [{"content": "cat dog bird"}, {"content": "fish turtle"}]
        results = self.semantic.search("cat", entries)
        assert len(results) >= 1

    def test_search_top_k(self) -> None:
        entries = [{"content": "a"}, {"content": "b"}, {"content": "c"}]
        results = self.semantic.search("a", entries, top_k=2)
        assert len(results) <= 2

    def test_reset(self) -> None:
        self.semantic.search("x", [{"content": "x"}])
        self.semantic.reset()
        assert self.semantic.search_count == 0


class TestKeywordSearch:
    def setup_method(self) -> None:
        self.kw = KeywordSearch()

    def test_search(self) -> None:
        entries = [{"content": "hello world"}, {"content": "goodbye"}]
        results = self.kw.search("hello", entries)
        assert len(results) == 1

    def test_search_exact(self) -> None:
        entries = [{"content": "hello world"}, {"content": "hello"}]
        results = self.kw.search_exact("hello world", entries)
        assert len(results) == 1

    def test_search_tags(self) -> None:
        entries = [{"tags": ["urgent", "work"]}, {"tags": ["personal"]}]
        results = self.kw.search_tags(["urgent"], entries)
        assert len(results) == 1

    def test_reset(self) -> None:
        self.kw.search("x", [{"content": "x"}])
        self.kw.reset()
        assert self.kw.search_count == 0


class TestGraphSearch:
    def setup_method(self) -> None:
        self.gs = GraphSearch()

    def test_search(self) -> None:
        entries = [{"content": "hello", "related": []}, {"content": "world", "related": []}]
        results = self.gs.search("hello", entries)
        assert len(results) == 1

    def test_bfs(self) -> None:
        graph = {"a": ["b", "c"], "b": ["d"], "c": [], "d": []}
        order = self.gs.bfs("a", graph, max_depth=2)
        assert "a" in order
        assert "d" in order

    def test_dfs(self) -> None:
        graph = {"a": ["b"], "b": ["c"], "c": []}
        order = self.gs.dfs("a", graph)
        assert order == ["a", "b", "c"]

    def test_reset(self) -> None:
        self.gs.search("x", [{"content": "x"}])
        self.gs.reset()
        assert self.gs.search_count == 0


class TestRanking:
    def setup_method(self) -> None:
        self.ranking = Ranking()

    def test_rank(self) -> None:
        items = [{"score": 0.5}, {"score": 1.0}, {"score": 0.2}]
        ranked = self.ranking.rank(items)
        assert ranked[0]["score"] == 1.0
        assert ranked[0]["rank"] == 1

    def test_top_k(self) -> None:
        items = [{"i": 1}, {"i": 2}, {"i": 3}]
        assert len(self.ranking.top_k(items, 2)) == 2

    def test_reset(self) -> None:
        self.ranking.rank([{"score": 1}])
        self.ranking.reset()
        assert self.ranking.ranking_count == 0


class TestReranking:
    def setup_method(self) -> None:
        self.reranking = Reranking()

    def test_rerank(self) -> None:
        items = [{"content": "hello world"}, {"content": "goodbye"}]
        results = self.reranking.rerank("world", items)
        assert len(results) == 2

    def test_reset(self) -> None:
        self.reranking.rerank("x", [{"content": "x"}])
        self.reranking.reset()
        assert self.reranking.reranking_count == 0


class TestScoring:
    def setup_method(self) -> None:
        self.scoring = Scoring()

    def test_score(self) -> None:
        items = [{"content": "hello world"}, {"content": "goodbye"}]
        scored = self.scoring.score("hello", items)
        assert "score" in scored[0]

    def test_score_boolean(self) -> None:
        items = [{"content": "hello world"}, {"content": "goodbye"}]
        scored = self.scoring.score_boolean("hello", items)
        assert scored[0]["score"] == 1.0
        assert scored[1]["score"] == 0.0

    def test_score_weighted(self) -> None:
        items = [{"content": "hello world", "title": "hi"}, {"content": "goodbye", "title": "bye"}]
        scored = self.scoring.score_weighted("hello", items, {"content": 0.7, "title": 0.3})
        assert "score" in scored[0]

    def test_reset(self) -> None:
        self.scoring.score("x", [{"content": "x"}])
        self.scoring.reset()
        assert self.scoring.scoring_count == 0


class TestRelevance:
    def setup_method(self) -> None:
        self.rel = Relevance()

    def test_compute(self) -> None:
        items = [{"content": "hello world"}, {"content": "goodbye world"}]
        results = self.rel.compute("hello", items)
        assert "relevance" in results[0]

    def test_threshold(self) -> None:
        items = [{"relevance": 0.8}, {"relevance": 0.3}]
        filtered = self.rel.threshold(items, 0.5)
        assert len(filtered) == 1

    def test_feedback_adjust(self) -> None:
        items = [{"id": "a", "relevance": 0.5}, {"id": "b", "relevance": 0.5}]
        adjusted = self.rel.feedback_adjust(items, ["a"], 0.3)
        assert adjusted[0]["relevance"] == 0.8

    def test_reset(self) -> None:
        self.rel.compute("x", [{"content": "x"}])
        self.rel.reset()
        assert self.rel.relevance_count == 0
