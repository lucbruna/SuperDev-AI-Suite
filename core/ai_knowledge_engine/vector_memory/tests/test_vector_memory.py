import pytest
import math
from ..vector_engine import VectorEngine, EngineConfig
from ..index_manager import IndexManager
from ..similarity_search import SimilaritySearch
from ..retrieval import RetrievalEngine
from ..memory_optimizer import MemoryOptimizer


class TestVectorEngine:
    @pytest.fixture
    async def engine(self):
        eng = VectorEngine(EngineConfig(dimension=4))
        await eng.initialize()
        yield eng
        await eng.stop()

    def test_initial_state(self, engine):
        assert engine.state.initialized is True
        assert engine.state.vector_count == 0

    def test_store_and_search(self, engine):
        vid = asyncio_run(engine.store([1.0, 0.0, 0.0, 0.0], {"label": "x-axis"}))
        assert vid is not None
        results = asyncio_run(engine.search([1.0, 0.0, 0.0, 0.0], top_k=5))
        assert len(results) == 1
        assert results[0][0] == vid
        assert abs(results[0][1] - 1.0) < 0.001

    def test_delete(self, engine):
        vid = asyncio_run(engine.store([1.0, 1.0, 1.0, 1.0]))
        assert asyncio_run(engine.delete(vid)) is True
        assert asyncio_run(engine.delete("nonexistent")) is False
        assert engine.state.vector_count == 0

    def test_index(self, engine):
        vectors = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0]]
        ids = asyncio_run(engine.index(vectors, [{"a": 1}, {"b": 2}]))
        assert len(ids) == 2
        assert engine.state.vector_count == 2

    def test_get_stats(self, engine):
        stats = asyncio_run(engine.get_stats())
        assert stats["state"]["initialized"] is True
        assert stats["config"]["dimension"] == 4
        assert stats["metrics"]["total_stored"] == 0


class TestIndexManager:
    def test_create_and_list_indexes(self):
        mgr = IndexManager()
        info = mgr.create_index("test_idx", "hnsw", 64)
        assert info.name == "test_idx"
        assert info.index_type == "hnsw"
        assert info.dimension == 64
        indexes = mgr.list_indexes()
        assert len(indexes) == 1

    def test_rebuild_index(self):
        mgr = IndexManager()
        info = mgr.create_index("idx")
        assert mgr.rebuild_index(info.index_id, {"v1": [1.0, 2.0]}) is True
        rebuilt = mgr.get_index_info(info.index_id)
        assert rebuilt.vector_count == 1
        assert mgr.rebuild_index("bad") is False

    def test_optimize_index(self):
        mgr = IndexManager()
        info = mgr.create_index("idx")
        assert mgr.optimize_index(info.index_id) is True
        assert mgr.optimize_index("bad") is False

    def test_get_index_info(self):
        mgr = IndexManager()
        assert mgr.get_index_info("nonexistent") is None


class TestSimilaritySearch:
    def test_search_by_vector(self):
        ss = SimilaritySearch()
        ss.add_vector("v1", [1.0, 0.0, 0.0], "hello world")
        ss.add_vector("v2", [0.0, 1.0, 0.0], "foo bar")
        results = ss.search_by_vector([1.0, 0.0, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0].id == "v1"
        assert results[0].score > results[1].score

    def test_search_by_text(self):
        ss = SimilaritySearch()
        ss.add_vector("v1", [1.0, 0.0, 0.0], "the quick brown fox")
        ss.add_vector("v2", [0.0, 1.0, 0.0], "jumps over the lazy dog")
        results = ss.search_by_text("brown fox", top_k=2)
        assert len(results) == 2
        assert results[0].id == "v1"

    def test_rank_results(self):
        ss = SimilaritySearch()
        from ..similarity_search import SearchResult
        results = [
            SearchResult(id="a", score=0.3),
            SearchResult(id="b", score=0.9),
        ]
        ranked = ss.rank_results(results)
        assert ranked[0].id == "b"

    def test_get_similarity_score(self):
        ss = SimilaritySearch()
        score = ss.get_similarity_score([1.0, 0.0], [0.0, 1.0])
        assert abs(score) < 0.001
        score2 = ss.get_similarity_score([1.0, 0.0], [1.0, 0.0])
        assert abs(score2 - 1.0) < 0.001


class TestRetrievalEngine:
    def test_retrieve_by_id(self):
        re = RetrievalEngine()
        re.add_document("d1", [1.0, 0.0, 0.0], {"title": "doc1"})
        doc = re.retrieve_by_id("d1")
        assert doc is not None
        assert doc.id == "d1"
        assert doc.metadata["title"] == "doc1"
        assert re.retrieve_by_id("nonexistent") is None

    def test_batch_retrieve(self):
        re = RetrievalEngine()
        re.add_document("a", [1.0, 0.0])
        re.add_document("b", [0.0, 1.0])
        docs = re.batch_retrieve(["a", "b", "nonexistent"])
        assert len(docs) == 2

    def test_retrieve_by_metadata(self):
        re = RetrievalEngine()
        re.add_document("d1", [1.0, 0.0], {"type": "doc"})
        re.add_document("d2", [0.0, 1.0], {"type": "img"})
        docs = re.retrieve_by_metadata({"type": "doc"})
        assert len(docs) == 1
        assert docs[0].id == "d1"

    def test_retrieve_similar(self):
        re = RetrievalEngine()
        re.add_document("d1", [1.0, 0.0, 0.0])
        re.add_document("d2", [1.0, 0.1, 0.0])
        re.add_document("d3", [0.0, 1.0, 0.0])
        similar = re.retrieve_similar("d1", top_k=2)
        assert len(similar) == 2
        assert similar[0].id == "d2"
        assert re.retrieve_similar("nonexistent") == []


class TestMemoryOptimizer:
    def test_optimize(self):
        opt = MemoryOptimizer()
        vectors = {"v1": [1.123456789, 2.987654321], "v2": [3.555555555, 4.111111111]}
        result = opt.optimize(vectors)
        assert len(result) == 2
        stats = opt.get_optimization_stats()
        assert len(stats) == 1
        assert stats[0].original_vectors == 2

    def test_prune(self):
        opt = MemoryOptimizer()
        vectors = {"v1": [0.001, 0.001], "v2": [1.0, 2.0]}
        result = opt.prune(vectors, threshold=0.01)
        assert "v1" not in result
        assert "v2" in result

    def test_compact(self):
        opt = MemoryOptimizer()
        vectors = {"v1": [1.23456789, 2.3456789]}
        result = opt.compact(vectors)
        assert len(result) == 1

    def test_defragment(self):
        opt = MemoryOptimizer()
        vectors = {"z": [1.0], "a": [2.0], "m": [3.0]}
        result = opt.defragment(vectors)
        assert list(result.keys()) == ["a", "m", "z"]


def asyncio_run(coro):
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as pool:
        future = pool.submit(asyncio.run, coro)
        return future.result()
