"""Tests for the knowledge rag subsystem."""

from __future__ import annotations

import pytest

from knowledge.knowledge_models import RetrievalContext, SearchResult
from knowledge.rag import (
    CitationManager,
    ContextBuilder,
    PromptBuilder,
    RagEngine,
    Reranker,
    ResponseGenerator,
    Retriever,
)


def _make_result(text: str, score: float, document_id: str = "") -> SearchResult:
    return SearchResult(text=text, score=score, source="test", document_id=document_id)


def _dummy_search(query: str, top_k: int = 5) -> list[SearchResult]:
    return [_make_result("alpha response", 0.95), _make_result("beta response", 0.20)]


class TestRetriever:
    def test_retrieve_with_threshold(self) -> None:
        retriever = Retriever(search_fn=_dummy_search, threshold=0.5)
        results = retriever.retrieve("query")
        assert [result.text for result in results] == ["alpha response"]

    def test_retrieve_sorts_by_score(self) -> None:
        retriever = Retriever(search_fn=_dummy_search)
        results = retriever.retrieve("query", top_k=2)
        assert results[0].score >= results[1].score

    def test_retrieve_without_search_fn(self) -> None:
        retriever = Retriever()
        assert retriever.retrieve("anything") == []


class TestCitationManager:
    def test_register_and_format(self) -> None:
        manager = CitationManager()
        manager.register([_make_result("fonte um", 0.9, "doc-a"), _make_result("fonte dois", 0.8, "doc-b")])
        formatted = manager.format_sources()
        assert len(formatted) == 2
        assert formatted[0].startswith("1. fonte um")

    def test_register_deduplicates(self) -> None:
        manager = CitationManager()
        manager.register([_make_result("dup", 0.9, "doc-x")])
        manager.register([_make_result("dup", 0.7, "doc-x")])
        assert len(manager.format_sources()) == 1

    def test_cite(self) -> None:
        manager = CitationManager()
        result = _make_result("fonte", 0.9, "doc-1")
        manager.register([result])
        assert manager.cite(result) == "[1]"
        assert manager.cite(_make_result("outra", 0.5)) == ""


class TestContextBuilder:
    def test_build(self) -> None:
        builder = ContextBuilder()
        context = builder.build("pergunta", [_make_result("texto", 0.9)])
        assert context.query == "pergunta"
        assert len(context.results) == 1
        assert context.memory_hits == []

    def test_truncate(self) -> None:
        builder = ContextBuilder()
        context = builder.build("q", [_make_result("a", 0.9), _make_result("b", 0.8)])
        truncated = builder.truncate(context, limit=1)
        assert len(truncated.results) == 1


class TestPromptBuilder:
    def test_build(self) -> None:
        builder = PromptBuilder()
        context = RetrievalContext(query="q", results=[_make_result("conteudo", 0.9)])
        prompt = builder.build("q", context)
        assert "system" in prompt
        assert "conteudo" in prompt["user"]


class TestReranker:
    def test_rerank_boosts_overlap(self) -> None:
        reranker = Reranker(keyword_bonus=0.1)
        results = [_make_result("relatorio financeiro trimestral", 0.5)]
        reranked = reranker.rerank("financeiro", results, top_k=1)
        assert reranked[0].score > 0.5

    def test_rerank_top_k(self) -> None:
        reranker = Reranker()
        results = [_make_result("a", 0.9), _make_result("b", 0.8)]
        assert len(reranker.rerank("q", results, top_k=1)) == 1


class TestResponseGenerator:
    def test_generate(self) -> None:
        generator = ResponseGenerator()
        context = RetrievalContext(
            query="Como X funciona?",
            results=[_make_result("Segundo a fonte, X funciona assim.", 0.9, "doc-1")],
        )
        result = generator.generate("Como X funciona?", context)
        assert result["answer"] == "Segundo a fonte, X funciona assim."
        assert result["used_sources"] == ["test"]
        assert result["score"] == pytest.approx(0.9)

    def test_generate_without_context(self) -> None:
        generator = ResponseGenerator()
        context = RetrievalContext(query="pergunta")
        result = generator.generate("pergunta", context)
        assert result["answer"]
        assert result["used_sources"] == []
        assert result["score"] == 0.0


class TestRagEngine:
    def test_pipeline(self) -> None:
        engine = RagEngine(retriever=Retriever(search_fn=_dummy_search))
        results, context, prompt, response = engine.pipeline("o que e a suite?", top_k=2)
        assert isinstance(results, list)
        assert isinstance(context, RetrievalContext)
        assert "system" in prompt
        assert response["answer"]

    def test_answer(self) -> None:
        engine = RagEngine(retriever=Retriever(search_fn=_dummy_search))
        answer = engine.answer("pergunta", top_k=2)
        assert answer["query"] == "pergunta"
        assert answer["answer"]
        assert "citations" in answer
        assert len(answer["scores"]) >= 1

    def test_pipeline_with_default_retriever(self) -> None:
        engine = RagEngine()
        results, context, prompt, response = engine.pipeline("nada")
        assert results == []
        assert response["used_sources"] == []
