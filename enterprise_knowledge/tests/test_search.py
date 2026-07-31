"""Tests for the search/ subsystem (Volume 27, Fase 5)."""

from __future__ import annotations

import pytest

from enterprise_knowledge.knowledge_factory import build_engine
from enterprise_knowledge.knowledge_models import (AccessLevel, SearchMode)
from enterprise_knowledge.search.filters import SearchFilters
from enterprise_knowledge.search.keyword_search import KeywordSearch
from enterprise_knowledge.search.ranking import SearchRanking
from enterprise_knowledge.search.search_engine import SearchEngine
from enterprise_knowledge.search.semantic_search import SemanticSearch
from enterprise_knowledge.search.suggestions import SearchSuggestions
from enterprise_knowledge.vector.vector_engine import VectorEngine


@pytest.fixture
def engine():
    engine = build_engine()
    vectors = VectorEngine(events=engine.events, metrics=engine.metrics,
                           config=engine.config, security=engine.security,
                           registry=engine.registry)
    engine.attach_subsystem("vector_engine", vectors)
    engine.attach_subsystem(
        "search_engine",
        SearchEngine(events=engine.events, metrics=engine.metrics,
                     config=engine.config, security=engine.security,
                     vectors=vectors))
    return engine


class TestKeywordSearch:
    def test_score_exact_overlap(self):
        search = KeywordSearch()
        assert search.score("sistema fiscal", "sistema fiscal 2026") > \
            search.score("sistema fiscal", "receita de bolo")

    def test_score_zero_when_no_overlap(self):
        assert KeywordSearch().score("abc", "xyz") == 0.0

    def test_search_returns_ranked(self):
        search = KeywordSearch()
        records = [
            {"id": "b", "text": "o sistema fiscal foi alterado"},
            {"id": "a", "text": "sistema fiscal sistema fiscal"},
            {"id": "c", "text": "receita de bolo"},
        ]
        results = search.search("sistema fiscal", records)
        assert [r["id"] for r in results] == ["a", "b"]

    def test_stopwords_ignored(self):
        search = KeywordSearch()
        assert search.score("de e o", "qualquer texto") == 0.0


class TestSemanticSearch:
    def test_empty_without_vectors(self):
        assert SemanticSearch().search("query") == []

    def test_delegates_to_vectors(self, engine):
        engine.vector_engine.add_text("sistema fiscal 2026",
                                      vector_id="vec-1",
                                      metadata={"text": "sistema fiscal 2026"})
        semantic = SemanticSearch(vectors=engine.vector_engine)
        results = semantic.search("fiscal", limit=5)
        assert results and results[0]["text"].startswith("sistema")


class TestSearchRanking:
    def test_fuse_combines_scores(self):
        ranking = SearchRanking(keyword_weight=0.5, semantic_weight=0.5)
        results = ranking.fuse(
            [{"id": "a", "text": "x", "score": 1.0}],
            [{"id": "a", "text": "x", "score": 0.5},
             {"id": "b", "text": "y", "score": 0.9}])
        assert results[0]["id"] == "a"
        assert results[0]["keyword_score"] == 1.0
        assert results[0]["semantic_score"] == 0.5
        assert len(results) == 2

    def test_rerank_bonus(self):
        ranking = SearchRanking()
        results = ranking.rerank(
            [{"id": "a", "text": "sistema fiscal", "score": 0.5},
             {"id": "b", "text": "qualquer coisa", "score": 0.8}],
            context="sistema fiscal")
        assert results[0]["id"] == "a"


class TestSearchFilters:
    def test_filter_by_metadata(self):
        filters = SearchFilters()
        results = [
            {"metadata": {"category": "code", "access_level": "public"}},
            {"metadata": {"category": "finance", "access_level": "public"}},
        ]
        kept = filters.apply(results, filters={"category": "code"})
        assert len(kept) == 1

    def test_min_access_filters_restricted(self):
        filters = SearchFilters()
        results = [
            {"metadata": {"access_level": "public"}},
            {"metadata": {"access_level": "restricted"}},
        ]
        assert len(filters.apply(results, min_access=AccessLevel.INTERNAL)) == 1


class TestSearchSuggestions:
    def test_prefix_suggestions(self):
        suggestions = SearchSuggestions(["fiscal", "financeiro", "fatura"])
        assert suggestions.suggest("fis") == ["fiscal"]
        assert suggestions.suggest("fin") == ["financeiro"]
        assert suggestions.suggest("fat") == ["fatura"]

    def test_empty_prefix(self):
        assert SearchSuggestions().suggest("") == []

    def test_learn_from_texts(self):
        suggestions = SearchSuggestions()
        suggestions.learn(["módulo financeiro", "banco de dados"])
        assert "financeiro" in suggestions.suggest("fin")


class TestSearchEngine:
    def test_keyword_mode(self, engine):
        engine.vector_engine.add_text("sistema fiscal", vector_id="vec-1",
                                      metadata={"text": "sistema fiscal"})
        engine.vector_engine.add_text("receita de bolo", vector_id="vec-2",
                                      metadata={"text": "receita de bolo"})
        results = engine.search_engine.search("fiscal",
                                              mode=SearchMode.KEYWORD)
        assert results and results[0]["text"] == "sistema fiscal"

    def test_semantic_mode(self, engine):
        engine.vector_engine.add_text("problema de performance do banco",
                                      vector_id="vec-1",
                                      metadata={"text":
                                                "problema de performance"})
        results = engine.search_engine.search("performance",
                                              mode=SearchMode.SEMANTIC)
        assert results

    def test_hybrid_default(self, engine):
        engine.vector_engine.add_text("ERP módulo fiscal", vector_id="vec-1",
                                      metadata={"text": "ERP módulo fiscal"})
        results = engine.search_engine.search("fiscal")
        assert results

    def test_filters_in_search(self, engine):
        engine.vector_engine.add_text("texto publico", vector_id="vec-1",
                                      metadata={"text": "texto publico",
                                                "access_level": "public"})
        engine.vector_engine.add_text("texto restrito", vector_id="vec-2",
                                      metadata={"text": "texto restrito",
                                                "access_level": "restricted"})
        results = engine.search_engine.search(
            "texto", mode=SearchMode.KEYWORD,
            min_access=AccessLevel.INTERNAL)
        assert len(results) == 1

    def test_metrics_and_events(self, engine):
        from enterprise_knowledge.knowledge_events import (
            EnterpriseKnowledgeEventType)
        seen = []
        engine.events.on(EnterpriseKnowledgeEventType.SEARCH_EXECUTED,
                         lambda payload: seen.append(payload))
        engine.search_engine.search("algo")
        assert engine.metrics.snapshot()["counters"].get(
            "ek.searches", 0) == 1
        assert seen and seen[0]["query"] == "algo"

    def test_suggest_and_learn(self, engine):
        engine.search_engine.learn(["módulo financeiro", "fatura fiscal"])
        suggestions = engine.search_engine.suggest("f")
        assert suggestions
        assert engine.search_engine.stats()["vocabulary"] >= 3
