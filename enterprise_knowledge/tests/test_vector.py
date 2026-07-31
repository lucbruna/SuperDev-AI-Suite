"""Tests for the vector/ subsystem (Volume 27, Fase 3)."""

from __future__ import annotations

import threading

import pytest

from enterprise_knowledge.knowledge_factory import build_engine
from enterprise_knowledge.knowledge_events import EnterpriseKnowledgeEventType
from enterprise_knowledge.knowledge_models import MemoryType
from enterprise_knowledge.vector.embedding_manager import EmbeddingManager
from enterprise_knowledge.vector.indexing import VectorIndexing
from enterprise_knowledge.vector.retrieval import VectorRetrieval
from enterprise_knowledge.vector.similarity_search import (SimilaritySearch,
                                                           cosine)
from enterprise_knowledge.vector.vector_database import VectorDatabase
from enterprise_knowledge.vector.vector_engine import VectorEngine


@pytest.fixture
def engine():
    engine = build_engine()
    engine.attach_subsystem(
        "vector_engine",
        VectorEngine(events=engine.events, metrics=engine.metrics,
                     config=engine.config, security=engine.security,
                     registry=engine.registry))
    return engine


class TestEmbeddingManager:
    def test_deterministic(self):
        embeddings = EmbeddingManager()
        assert embeddings.embed("índice SQL") == \
            embeddings.embed("índice SQL")

    def test_normalized(self):
        vector = EmbeddingManager().embed("sistema fiscal")
        norm = sum(v * v for v in vector) ** 0.5
        assert norm == pytest.approx(1.0)

    def test_similar_texts_close(self):
        embeddings = EmbeddingManager()
        a = embeddings.embed("como resolver problema de performance")
        b = embeddings.embed("como resolver problemas de performance")
        c = embeddings.embed("café da manhã com pão")
        assert cosine(a, b) > cosine(a, c)

    def test_empty_text(self):
        assert EmbeddingManager().embed("") == [0.0] * 32

    def test_custom_dimensions(self):
        assert len(EmbeddingManager(dimensions=16).embed("ERP")) == 16


class TestSimilarity:
    def test_identical_vectors(self):
        v = [0.6, 0.8, 0.0]
        assert cosine(v, v) == pytest.approx(1.0)

    def test_orthogonal(self):
        assert cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_rank_orders_by_score(self):
        search = SimilaritySearch(metric="cosine")
        query = [1.0, 0.0, 0.0]
        candidates = [
            {"id": "b", "vector": [0.1, 1.0, 0.0]},
            {"id": "a", "vector": [0.9, 0.1, 0.0]},
            {"id": "c", "vector": [0.001, 0.0, 1.0]},
        ]
        results = search.rank(query, candidates)
        assert [r["id"] for r in results] == ["a", "b", "c"]

    def test_rank_limit(self):
        search = SimilaritySearch()
        candidates = [{"vector": [0.9]} for _ in range(5)]
        assert len(search.rank([1.0], candidates, limit=2)) == 2


class TestVectorDatabase:
    def test_upsert_and_get(self):
        database = VectorDatabase()
        database.upsert("vec-1", [0.5, 0.5], {"text": "nota"})
        assert database.get("vec-1") == [0.5, 0.5]
        assert database.metadata_for("vec-1")["text"] == "nota"

    def test_all_returns_copies(self):
        database = VectorDatabase()
        database.upsert("vec-1", [1.0, 0.0], {"text": "x"})
        item = database.all()[0]
        item["vector"][0] = 999.0
        stored = database.get("vec-1")
        assert stored is not None and stored[0] == 1.0

    def test_delete_clear_count(self):
        database = VectorDatabase()
        database.upsert("vec-1", [1.0])
        database.upsert("vec-2", [1.0])
        assert database.delete("vec-1") is True
        assert database.delete("vec-1") is False
        assert database.count() == 1
        database.clear()
        assert database.count() == 0

    def test_thread_safety(self):
        database = VectorDatabase()
        errors = []

        def worker(index):
            try:
                for offset in range(50):
                    database.upsert(f"vec-{index}-{offset}", [index])
                assert database.count() > 0
            except Exception as exc:  # pragma: no cover
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,))
                   for i in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert not errors

    def test_stats(self):
        database = VectorDatabase()
        database.upsert("vec-1", [0.5, 0.5])
        stats = database.stats()
        assert stats["vectors"] == 1 and stats["dimensions"] == 2


class TestVectorIndexing:
    def test_chunk_text(self):
        indexing = VectorIndexing(chunk_size=4)
        chunks = indexing.chunk("a b c d e f g")
        assert chunks == ["a b c d", "e f g"]

    def test_index_text_prefixes(self):
        indexing = VectorIndexing(chunk_size=2)
        entries = indexing.index_text(
            "palavra repetida palavra repetida", prefix="doc-1")
        assert all(entry["chunk_id"].startswith("doc-1-")
                   for entry in entries)
        assert len(entries) == 2
        assert len(entries[0]["vector"]) == 32


class TestVectorRetrieval:
    def test_filters_metadata(self):
        database = VectorDatabase()
        database.upsert("vec-1", [0.9, 0.0], {"text": "a", "tag": "x"})
        database.upsert("vec-2", [0.9, 0.0], {"text": "b", "tag": "y"})
        retrieval = VectorRetrieval(database=database)
        results = retrieval.search([1.0, 0.0], filters={"tag": "x"})
        assert [r["vector_id"] for r in results] == ["vec-1"]

    def test_threshold_filters(self):
        database = VectorDatabase()
        database.upsert("vec-1", [0.1, 0.5], {"text": "longe"})
        retrieval = VectorRetrieval(database=database)
        assert retrieval.search([1.0, 0.0], threshold=0.9) == []


class TestVectorEngine:
    def test_embed_and_store(self, engine):
        vector_engine = engine.vector_engine
        vector_id = vector_engine.add_text("nota de reunião", vector_id="vec-n1")
        assert vector_id == "vec-n1"
        assert vector_engine.database.count() == 1

    def test_auto_id(self, engine):
        vector_id = engine.vector_engine.add_text("texto sem id")
        assert vector_id.startswith("vec-")

    def test_add_document_chunks_and_event(self, engine):
        vector_engine = engine.vector_engine
        chunks = vector_engine.add_document(
            "doc-1", "o sistema fiscal foi alterado " * 300)
        assert len(chunks) >= 2
        assert "doc-1" in vector_engine.database.metadata_for(
            chunks[0]).get("document_id", "")
        assert engine.metrics.snapshot()["counters"].get(
            "ek.documents", 0) >= 1

    def test_query_returns_relevant_first(self, engine):
        vector_engine = engine.vector_engine
        vector_engine.add_text("sistema fiscal 2026", vector_id="vec-f",
                               metadata={"text": "sistema fiscal 2026"})
        vector_engine.add_text("receita de bolo", vector_id="vec-b",
                               metadata={"text": "receita de bolo"})
        results = vector_engine.query("sistema fiscal")
        assert results
        assert results[0]["vector_id"] == "vec-f"

    def test_answer_question_snippets(self, engine):
        vector_engine = engine.vector_engine
        vector_engine.add_document(
            "doc-q", "por que o módulo financeiro foi alterado")
        answer = vector_engine.answer_question("módulo financeiro")
        assert answer["question"] == "módulo financeiro"
        assert answer["snippets"]

    def test_delete(self, engine):
        vector_engine = engine.vector_engine
        vector_engine.add_text("temp", vector_id="vec-temp")
        assert vector_engine.delete("vec-temp") is True
        assert vector_engine.database.count() == 0

    def test_metrics_and_events(self, engine):
        vector_engine = engine.vector_engine
        seen = []
        engine.events.on(EnterpriseKnowledgeEventType.SEARCH_EXECUTED,
                         lambda payload: seen.append(payload))
        vector_engine.add_text("métrica", vector_id="vec-m")
        vector_engine.query("métrica")
        counters = engine.metrics.snapshot()["counters"]
        assert counters.get("ek.vectors", 0) >= 1
        assert counters.get("ek.searches", 0) == 1
        assert len(seen) == 1

    def test_stats(self, engine):
        vector_engine = engine.vector_engine
        vector_engine.add_text("x", vector_id="vec-x")
        stats = vector_engine.stats()
        assert stats["database"]["vectors"] == 1
        assert stats["embeddings"]["dimensions"] == 32
