"""Unit tests for phase 4 — embeddings, LLM client and RAG retriever.

Covers the hash embedder (determinism, normalization, dimensions), the vector
stores (ranking, remove, clear, JSON round-trip, persistence), the embedding
service analyzer hook (context integration + gating), the offline LLM fallback
and the RAG retriever/answer flow over an indexed fixture.
"""
from __future__ import annotations

import math

import pytest

from modules.ai_code_knowledge_graph.config.knowledge_config import KnowledgeConfig
from modules.ai_code_knowledge_graph.core.knowledge_context import KnowledgeContext
from modules.ai_code_knowledge_graph.core.knowledge_runtime import KnowledgeRuntime
from modules.ai_code_knowledge_graph.embeddings.embedder import HashEmbedder
from modules.ai_code_knowledge_graph.embeddings.service import EmbeddingService
from modules.ai_code_knowledge_graph.embeddings.vector_store import (
    MemoryVectorStore,
    PersistentVectorStore,
    cosine_similarity,
)
from modules.ai_code_knowledge_graph.graph import KnowledgeGraphBuilder
from modules.ai_code_knowledge_graph.llm.client import LLMClient
from modules.ai_code_knowledge_graph.rag.context import build_context
from modules.ai_code_knowledge_graph.rag.retriever import RagRetriever, _SYSTEM_PROMPT


# ------------------------------------------------------------------ fixtures
def _entity(kind: str, name: str, start_line: int = 1, end_line: int | None = None, **extra) -> dict:
    return {"kind": kind, "name": name, "start_line": start_line, "end_line": end_line or start_line, **extra}


def _file_entry(rel_path: str, language: str, entities: list[dict]) -> dict:
    return {
        "rel_path": rel_path,
        "language": language,
        "size": 1,
        "parsed": {"language": language, "rel_path": rel_path, "entities": entities, "error": None},
    }


def _scan_fixture() -> dict:
    files = [
        _file_entry("src/app.py", "python", [
            {"kind": "file", "name": "src/app.py", "start_line": 1, "end_line": 12, "line_count": 12},
            _entity("class", "App", 3, 12, methods=[_entity("method", "run", 4, 8)]),
            _entity("function", "main", 10, 12),
        ]),
        _file_entry("src/helpers.py", "python", [
            {"kind": "file", "name": "src/helpers.py", "start_line": 1, "end_line": 3, "line_count": 3},
            _entity("function", "helper", 1, 3),
        ]),
        _file_entry("db/schema.sql", "database", [
            {"kind": "file", "name": "db/schema.sql", "start_line": 1, "end_line": 4, "line_count": 4},
            _entity("table", "users", 1, 4),
        ]),
    ]
    return {"project_root": "/tmp/demo", "files": files, "errors": [], "stats": {"files": len(files)}}


# --------------------------------------------------------------- embedder
class TestHashEmbedder:
    def test_default_dimensions(self) -> None:
        assert HashEmbedder().dimensions == 256

    def test_custom_dimensions(self) -> None:
        assert HashEmbedder(dimensions=64).dimensions == 64

    def test_dimensions_minimum(self) -> None:
        with pytest.raises(ValueError):
            HashEmbedder(dimensions=4)

    def test_embed_length_and_normalization(self) -> None:
        vector = HashEmbedder(dimensions=64).embed("class User login logout")
        assert len(vector) == 64
        norm = math.sqrt(sum(value * value for value in vector))
        assert norm == pytest.approx(1.0)

    def test_deterministic(self) -> None:
        embedder = HashEmbedder()
        assert embedder.embed("def helper(x): return x") == embedder.embed("def helper(x): return x")

    def test_different_text_different_vector(self) -> None:
        embedder = HashEmbedder()
        assert embedder.embed("alpha") != embedder.embed("omega")


# ------------------------------------------------------------- vector store
class TestVectorStore:
    def test_cosine_similarity_basics(self) -> None:
        assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
        assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
        assert cosine_similarity([1.0], [1.0, 0.0]) == 0.0
        assert cosine_similarity([], []) == 0.0

    def test_search_ranks_by_similarity(self) -> None:
        store = MemoryVectorStore()
        store.add("alpha", [1.0, 0.0, 0.0], {"kind": "file"})
        store.add("beta", [0.0, 1.0, 0.0], {"kind": "file"})
        results = store.search([1.0, 0.0, 0.0], k=2)
        assert results[0][0] == "alpha"
        assert results[1][0] == "beta"
        assert results[0][2] == {"kind": "file"}

    def test_k_clamps_to_available(self) -> None:
        store = MemoryVectorStore()
        store.add("a", [1.0, 0.0], {"kind": "file"})
        assert store.search([1.0, 0.0], k=10) == [("a", pytest.approx(1.0), {"kind": "file"})]
        assert store.search([1.0, 0.0], k=0) == []

    def test_remove_and_clear(self) -> None:
        store = MemoryVectorStore()
        store.add("a", [1.0, 0.0], {"kind": "file"})
        store.add("b", [0.0, 1.0], {"kind": "file"})
        store.remove("a")
        assert store.size() == 1
        store.clear()
        assert store.size() == 0

    def test_json_round_trip(self) -> None:
        store = MemoryVectorStore()
        store.add("a", [1.0, 0.0], {"kind": "file", "file": "x.py"})
        restored = MemoryVectorStore.from_json(store.to_json())
        assert restored.size() == 1
        assert restored.search([1.0, 0.0], k=1)[0][0] == "a"

    def test_persistent_store_save_load(self, tmp_path) -> None:
        path = tmp_path / "vectors.json"
        store = PersistentVectorStore(path)
        store.add("a", [1.0, 0.0], {"kind": "file"})
        store.save()
        reloaded = PersistentVectorStore(path)
        assert reloaded.size() == 1
        assert reloaded.search([1.0, 0.0], k=1)[0][0] == "a"


# -------------------------------------------------------- embedding service
class TestEmbeddingService:
    def _indexed_context(self):
        config = KnowledgeConfig()
        ctx = KnowledgeContext(config=config)
        ctx.memory.put("scan_result", _scan_fixture())
        graph = KnowledgeGraphBuilder().build(_scan_fixture())
        ctx.memory.put("knowledge_graph", graph)
        return ctx, graph

    def test_index_embeds_files_and_definitions(self) -> None:
        ctx, graph = self._indexed_context()
        service = EmbeddingService()
        result = service.index(ctx)
        definition_kinds = {"class", "function", "method", "table"}
        expected = len(_scan_fixture()["files"]) + sum(
            1 for node in graph["nodes"] if node["kind"] in definition_kinds
        )
        assert result["items"] == expected
        assert ctx.memory.get("vector_store") is service.store
        assert ctx.stats["embeddings_items"] == expected

    def test_index_skips_when_disabled(self) -> None:
        ctx, _ = self._indexed_context()
        config = ctx.config
        config.run_embeddings = False
        service = EmbeddingService()
        result = service.index(ctx)
        assert result["items"] == 0
        assert ctx.memory.get("vector_store") is None

    def test_search_and_similar(self) -> None:
        ctx, _ = self._indexed_context()
        service = EmbeddingService()
        service.index(ctx)
        results = service.search("users", k=3)
        assert results and len(results[0]) == 3
        assert results[0][1] >= results[-1][1]
        similar = service.similar(results[0][0], k=2)
        assert similar  # the item is similar to itself


# ------------------------------------------------------------------- llm
class TestLLMClient:
    def test_echo_fallback_deterministic(self) -> None:
        client = LLMClient(provider="echo")
        assert client.complete("sys", "usr") == "ECHO[3:3]"
        assert client.complete("sys", "usr") == client.complete("sys", "usr")

    def test_echo_not_available(self) -> None:
        assert LLMClient(provider="echo").available is False

    def test_provider_without_key_returns_none(self) -> None:
        client = LLMClient(provider="openai")
        assert client.complete("sys", "usr") is None


# -------------------------------------------------------------------- rag
class TestRagRetriever:
    def _indexed_context(self):
        config = KnowledgeConfig()
        ctx = KnowledgeContext(config=config)
        ctx.memory.put("scan_result", _scan_fixture())
        graph = KnowledgeGraphBuilder().build(_scan_fixture())
        ctx.memory.put("knowledge_graph", graph)
        return ctx, graph

    def test_retrieve_returns_ranked_results(self) -> None:
        retriever = RagRetriever(EmbeddingService())
        # Index a minimal store directly for a deterministic query.
        store = retriever.embeddings.store
        store.clear()
        store.add("db/schema.sql", retriever.embeddings.embedder.embed("table users email"), {"kind": "file", "file": "db/schema.sql"})
        results = retriever.retrieve("users", k=5)
        assert results
        assert results[0][0] == "db/schema.sql"

    def test_ask_returns_answer_context_and_results(self) -> None:
        retriever = RagRetriever(EmbeddingService(), k=3)
        retriever.embeddings.store.clear()
        retriever.embeddings.store.add(
            "file:src/app.py",
            retriever.embeddings.embedder.embed("app main entry point"),
            {"kind": "file", "file": "src/app.py"},
        )
        result = retriever.ask("main", k=1)
        assert result["query"] == "main"
        assert result["answer"] == f"ECHO[{len(_SYSTEM_PROMPT)}:4]"
        assert "src/app.py" in result["context"]
        assert result["results"][0]["id"] == "file:src/app.py"

    def test_ask_without_results_has_no_answer(self) -> None:
        retriever = RagRetriever(EmbeddingService(), k=3)
        retriever.embeddings.store.clear()
        result = retriever.ask("anything")
        assert result["results"] == []
        assert result["answer"] is None

    def test_build_context(self) -> None:
        context = build_context([("a", 0.9, {"kind": "file", "name": "", "file": "x.py"})])
        assert "x.py" in context


# ------------------------------------------------ pipeline wiring (embeddings)
class TestPipelineWiring:
    def test_runtime_registers_embeddings_analyzer(self) -> None:
        config = KnowledgeConfig()
        runtime = KnowledgeRuntime(config)
        assert runtime.registry.has("analyzer", "embeddings")
