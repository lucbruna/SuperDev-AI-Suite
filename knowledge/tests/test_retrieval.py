"""Tests for the knowledge retrieval subsystem."""

from __future__ import annotations

import pytest

from knowledge.embeddings.generator import HashEmbeddingGenerator
from knowledge.knowledge_config import KnowledgeConfig
from knowledge.knowledge_models import Embedding, RetrievalContext, SearchResult
from knowledge.retrieval import (
    ContextAssembler,
    Fusion,
    Reranker,
    RetrievalEngine,
    Retriever,
)


def _result(text: str, score: float, source: str = "vector") -> SearchResult:
    return SearchResult(text=text, score=score, source=source)


class TestRetriever:
    def test_retrieve_from_vector(self) -> None:
        provider = HashEmbeddingGenerator(dimensions=64)
        retriever = Retriever(embedding_provider=provider)
        retriever.vector_store.add(
            Embedding(vector=provider.embed("retrieval pipeline content"), text="retrieval pipeline content", document_id="doc-1")
        )
        results = retriever.retrieve("pipeline", top_k=3)
        assert len(results) == 1
        assert results[0].document_id == "doc-1"

    def test_retrieve_merges_sources(self) -> None:
        from knowledge.memory.memory_storage import InMemoryMemoryStorage
        from knowledge.knowledge_models import MemoryRecord

        memory_store = InMemoryMemoryStorage()
        memory_store.save(MemoryRecord(content="deploy do servidor", importance=0.9))
        retriever = Retriever(memory_store=memory_store)
        results = retriever.retrieve("deploy", top_k=5)
        assert len(results) == 1
        assert results[0].source == "memory"

    def test_retrieve_without_sources(self) -> None:
        retriever = Retriever()
        assert retriever.retrieve("nada configurado") == []

    def test_retrieve_from_graph(self) -> None:
        from knowledge.knowledge_graph.graph import KnowledgeGraph
        from knowledge.knowledge_models import Relation

        graph = KnowledgeGraph()
        graph.add_relation(Relation(source="SuperDev", target="RAG"))
        retriever = Retriever(graph_engine=graph)
        results = retriever.retrieve("SuperDev", top_k=5)
        assert any(result.source == "graph" for result in results)


class TestFusion:
    def test_fuse_ranks_by_rrf(self) -> None:
        fusion = Fusion()
        first = [_result("alpha", 0.9), _result("beta", 0.8)]
        second = [_result("beta", 0.7), _result("gamma", 0.6)]
        fused = fusion.fuse([first, second])
        assert fused[0].text == "beta"
        assert fused[0].score > fused[1].score

    def test_fuse_merges_sources(self) -> None:
        fusion = Fusion()
        fused = fusion.fuse([[_result("x", 0.9, "keyword")], [_result("x", 0.8, "semantic")]])
        assert fused[0].source == "keyword+semantic"


class TestReranker:
    def test_rerank_boosts_overlap(self) -> None:
        reranker = Reranker(overlap_bonus=0.1)
        results = [_result("relatorio financeiro", 0.5)]
        reranked = reranker.rerank("financeiro", results)
        assert reranked[0].score > 0.5

    def test_rerank_top_k(self) -> None:
        reranker = Reranker()
        results = [_result("a", 0.9), _result("b", 0.8)]
        assert len(reranker.rerank("q", results, top_k=1)) == 1


class TestContextAssembler:
    def test_assemble(self) -> None:
        assembler = ContextAssembler()
        context = assembler.assemble("pergunta", [_result("texto", 0.9)], memory_hits=["m1"])
        assert context.query == "pergunta"
        assert len(context.results) == 1
        assert context.memory_hits == ["m1"]

    def test_truncate_by_limit_and_chars(self) -> None:
        assembler = ContextAssembler()
        context = assembler.assemble("q", [_result("aaaa", 0.9), _result("bbbb", 0.8)])
        assert len(assembler.truncate(context, limit=1).results) == 1
        assert len(assembler.truncate(context, chars=5).results) == 1


class TestRetrievalEngine:
    def test_retrieve_returns_context(self) -> None:
        provider = HashEmbeddingGenerator(dimensions=64)
        engine = RetrievalEngine(embedding_provider=provider, config=KnowledgeConfig(similarity_threshold=0.0))
        engine.vector_store.add(
            Embedding(vector=provider.embed("conteudo do retriever"), text="conteudo do retriever", document_id="doc-1")
        )
        context = engine.retrieve("retriever", top_k=3)
        assert isinstance(context, RetrievalContext)
        assert len(context.results) >= 1

    def test_retrieve_sources(self) -> None:
        engine = RetrievalEngine()
        sources = engine.retrieve_sources("qualquer coisa")
        assert set(sources.keys()) == {"vector", "memory", "graph"}
        assert sources["vector"] == []
