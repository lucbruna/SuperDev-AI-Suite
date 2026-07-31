"""Tests for the knowledge vector store subsystem."""

from __future__ import annotations

import pytest

from knowledge.knowledge_models import Embedding
from knowledge.vector_store import (
    CollectionManager,
    Filtering,
    HybridSearch,
    IndexManager,
    InMemoryVectorStorage,
    Ranking,
    SimilaritySearch,
    VectorEngine,
)


def _unit_vector(value: float, size: int = 8) -> list[float]:
    vector = [0.0] * size
    vector[0] = value
    return vector


class TestInMemoryVectorStorage:
    def test_add_search_identical(self) -> None:
        store = InMemoryVectorStorage()
        embedding_id = store.add(Embedding(vector=_unit_vector(1.0), text="alpha", document_id="doc-1"))
        assert embedding_id == "vec-1"
        results = store.search(_unit_vector(1.0))
        assert len(results) == 1
        assert results[0].text == "alpha"
        assert results[0].document_id == "doc-1"
        assert results[0].score == pytest.approx(1.0)

    def test_search_different_vector(self) -> None:
        store = InMemoryVectorStorage()
        store.add(Embedding(vector=_unit_vector(1.0), text="alpha"))
        # cosine([0.0, 1.0, 0, ...], [1.0, 0, 0, ...]) == 0.0, passes threshold 0.0
        results = store.search([0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        assert len(results) == 1
        assert results[0].score == pytest.approx(0.0)

    def test_threshold_filters(self) -> None:
        store = InMemoryVectorStorage(threshold=0.5)
        store.add(Embedding(vector=_unit_vector(1.0), text="near"))
        store.add(Embedding(vector=_unit_vector(-1.0), text="far"))
        results = store.search(_unit_vector(1.0))
        assert [result.text for result in results] == ["near"]

    def test_delete_and_count(self) -> None:
        store = InMemoryVectorStorage()
        embedding_id = store.add(Embedding(vector=_unit_vector(1.0), text="x"))
        assert store.count() == 1
        assert store.delete(embedding_id) is True
        assert store.count() == 0
        assert store.delete(embedding_id) is False

    def test_get(self) -> None:
        store = InMemoryVectorStorage()
        embedding_id = store.add(Embedding(vector=[1.0], text="stored"))
        stored = store.get(embedding_id)
        assert stored is not None
        assert stored.text == "stored"
        assert store.get("missing") is None

    def test_serialization_roundtrip(self) -> None:
        store = InMemoryVectorStorage()
        store.add(Embedding(vector=[1.0, 0.0], text="saved"))
        data = store.to_dict()
        restored = InMemoryVectorStorage()
        restored.load_dict(data)
        assert restored.count() == 1


class TestSimilaritySearch:
    def test_search_scores(self) -> None:
        searcher = SimilaritySearch()
        embeddings = [
            Embedding(vector=_unit_vector(1.0), text="one"),
            Embedding(vector=_unit_vector(0.5), text="half"),
            Embedding(vector=_unit_vector(-1.0), text="minus"),
        ]
        results = searcher.search(_unit_vector(1.0), embeddings, top_k=2)
        assert [result.text for result in results] == ["one", "half"]

    def test_methods(self) -> None:
        dot = SimilaritySearch(method="dot")
        euclidean = SimilaritySearch(method="euclidean")
        embeddings = [Embedding(vector=[1.0, 0.0], text="x")]
        assert len(dot.search([1.0, 0.0], embeddings)) == 1
        assert len(euclidean.search([1.0, 0.0], embeddings)) == 1


class TestFiltering:
    def test_metadata_filter(self) -> None:
        filtering = Filtering()
        results = [
            SearchResultLike(text="a", metadata={"lang": "pt"}),
            SearchResultLike(text="b", metadata={"lang": "en"}),
        ]
        filtered = filtering.apply(results, metadata_eq={"lang": "pt"})
        assert [result.text for result in filtered] == ["a"]

    def test_score_filter(self) -> None:
        filtering = Filtering()
        results = [
            SearchResultLike(text="a", score=0.9),
            SearchResultLike(text="b", score=0.3),
        ]
        assert len(filtering.apply_score(results, 0.5)) == 1


class TestRanking:
    def test_sort_and_top_k(self) -> None:
        ranking = Ranking()
        results = [
            SearchResultLike(text="a", score=0.3),
            SearchResultLike(text="b", score=0.9),
        ]
        sorted_results = ranking.sort_by_score(results)
        assert sorted_results[0].text == "b"
        assert [r.text for r in ranking.top_k(sorted_results, 1)] == ["b"]

    def test_deduplicate(self) -> None:
        ranking = Ranking()
        results = [
            SearchResultLike(text="same", score=0.9),
            SearchResultLike(text="SAME", score=0.5),
        ]
        assert len(ranking.deduplicate(results)) == 1


class TestCollectionManager:
    def test_create_add_search(self) -> None:
        manager = CollectionManager()
        assert manager.create("docs") is True
        assert manager.create("docs") is False
        manager.add("docs", Embedding(vector=_unit_vector(1.0), text="alpha"))
        manager.add("docs", Embedding(vector=_unit_vector(-1.0), text="beta"))
        assert manager.count("docs") == 2
        results = manager.search("docs", _unit_vector(1.0))
        assert results[0].text == "alpha"
        assert manager.list() == ["docs"]

    def test_delete(self) -> None:
        manager = CollectionManager()
        manager.create("a")
        assert manager.delete("a") is True
        assert manager.delete("a") is False


class TestIndexManager:
    def test_add_search_delete(self) -> None:
        manager = IndexManager()
        embedding_id = manager.add(Embedding(vector=_unit_vector(1.0), text="indexed"))
        assert manager.count() == 1
        results = manager.search(_unit_vector(1.0))
        assert results[0].text == "indexed"
        assert manager.delete(embedding_id) is True
        assert manager.count() == 0


class TestHybridSearch:
    def test_fuses_vector_and_keyword(self) -> None:
        search = HybridSearch()
        texts = ["busca vetorial embeddings", "relatorio financeiro trimestral"]
        vectors = [_unit_vector(1.0), _unit_vector(-1.0)]
        results = search.search("busca vetorial", _unit_vector(1.0), texts, vectors, top_k=2)
        assert len(results) == 2
        assert results[0].source == "hybrid"
        assert results[0].text == "busca vetorial embeddings"


class TestVectorEngine:
    def test_add_search_stats(self) -> None:
        engine = VectorEngine()
        embedding_id = engine.add(Embedding(vector=_unit_vector(1.0), text="alpha", document_id="doc-1"))
        assert embedding_id.startswith("vec-")
        results = engine.search(_unit_vector(1.0))
        assert results[0].text == "alpha"
        stats = engine.stats()
        assert stats["vectors"] == 1
        engine.clear()
        assert engine.stats()["vectors"] == 0

    def test_search_in_collection(self) -> None:
        engine = VectorEngine()
        engine.add(Embedding(vector=_unit_vector(1.0), text="a"), collection="c1")
        results = engine.search(_unit_vector(1.0), collection="c1")
        assert results[0].text == "a"
        assert engine.stats()["collections"] == ["c1"]


class SearchResultLike:
    def __init__(self, text: str, metadata=None, score: float = 0.0) -> None:
        self.text = text
        self.metadata = metadata or {}
        self.score = score
        self.source = "test"
        self.document_id = ""
