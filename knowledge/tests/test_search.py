"""Tests for the knowledge search subsystem."""

from __future__ import annotations

import pytest

from knowledge.embeddings.generator import HashEmbeddingGenerator
from knowledge.knowledge_models import Embedding, SearchResult
from knowledge.search import (
    KeywordSearch,
    QueryParser,
    ResultRanker,
    SearchEngine,
    SearchManager,
    SemanticSearch,
)
from knowledge.vector_store.storage import InMemoryVectorStorage


class TestQueryParser:
    def test_keywords(self) -> None:
        parser = QueryParser()
        assert parser.keywords("Busca  Vetorial") == ["busca", "vetorial"]

    def test_filters(self) -> None:
        parser = QueryParser()
        assert parser.filters("busca lang:pt topic:rag") == {"lang": "pt", "topic": "rag"}

    def test_clean_query(self) -> None:
        parser = QueryParser()
        assert parser.clean_query("busca lang:pt") == "busca"
        parser_no_strip = QueryParser(strip_filters=False)
        assert parser_no_strip.clean_query("busca lang:pt") == "busca lang:pt"


class TestKeywordSearch:
    def test_search_over_index(self) -> None:
        search = KeywordSearch()
        search.index_manager.add("doc-1", "configuracao de deploy no servidor", {"lang": "pt"})
        search.index_manager.add("doc-2", "relatorio financeiro trimestral")
        results = search.search("deploy")
        assert len(results) == 1
        assert results[0].document_id == "doc-1"
        assert results[0].source == "keyword"
        assert results[0].score > 0


class TestSemanticSearch:
    def test_search_with_embedding_provider(self) -> None:
        provider = HashEmbeddingGenerator(dimensions=64)
        store = InMemoryVectorStorage()
        search = SemanticSearch(vector_store=store, embedding_provider=provider)
        store.add(Embedding(vector=provider.embed("semantic retrieval content"), text="semantic retrieval content", document_id="doc-1"))
        results = search.search("retrieval", top_k=5, threshold=0.0)
        assert len(results) == 1
        assert results[0].document_id == "doc-1"

    def test_search_without_provider(self) -> None:
        search = SemanticSearch()
        assert search.search("anything") == []


class TestResultRanker:
    def test_fuse(self) -> None:
        ranker = ResultRanker()
        keyword_hits = [SearchResult(text="alpha", score=1.0, source="keyword")]
        semantic_hits = [SearchResult(text="alpha", score=0.5, source="semantic")]
        fused = ranker.fuse(keyword_hits, semantic_hits)
        assert fused[0].text == "alpha"
        assert fused[0].score == pytest.approx(1.0 * 0.3 + 0.5 * 0.7)
        assert fused[0].source == "keyword+semantic"

    def test_top_k(self) -> None:
        ranker = ResultRanker()
        results = [SearchResult(text="a", score=0.9), SearchResult(text="b", score=0.8)]
        assert len(ranker.top_k(results, 1)) == 1
        assert len(ranker.top_k(results, 10)) == 2


class TestSearchEngine:
    def test_keyword_search(self) -> None:
        engine = SearchEngine()
        engine.index_manager.add("doc-1", "o deploy do servidor falhou", {"lang": "pt"})
        results = engine.search("deploy")
        assert len(results) == 1
        assert results[0].document_id == "doc-1"

    def test_semantic_and_keyword_fusion(self) -> None:
        provider = HashEmbeddingGenerator(dimensions=64)
        engine = SearchEngine(embedding_provider=provider)
        engine.vector_store.add(Embedding(vector=provider.embed("retrieval augmented generation"), text="retrieval augmented generation", document_id="doc-1"))
        engine.index_manager.add("doc-1", "retrieval augmented generation", {})
        results = engine.search("retrieval")
        assert len(results) == 1
        assert results[0].document_id == "doc-1"


class TestSearchManager:
    def test_search_and_modes(self) -> None:
        manager = SearchManager()
        manager.engine.index_manager.add("doc-1", "conteudo de busca indexado")
        assert len(manager.search("busca")) == 1
        assert len(manager.keyword_only("conteudo")) == 1
        assert manager.semantic_only("busca") == []

    def test_stats(self) -> None:
        manager = SearchManager()
        manager.engine.index_manager.add("doc-1", "texto para estatisticas")
        stats = manager.stats()
        assert stats["index_terms"] >= 1
        assert stats["vectors"] == 0
