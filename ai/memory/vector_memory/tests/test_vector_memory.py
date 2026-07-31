from __future__ import annotations

from ..backup import Backup
from ..cache import Cache
from ..embedding_manager import EmbeddingManager
from ..embedding_repository import EmbeddingRepository
from ..optimizer import Optimizer
from ..reranker import Reranker
from ..restore import Restore
from ..retrieval_engine import RetrievalEngine
from ..similarity_engine import SimilarityEngine
from ..statistics import Statistics
from ..vector_store import VectorStore


class TestVectorStore:
    def setup_method(self) -> None:
        self.store = VectorStore()

    def test_insert_and_get(self) -> None:
        self.store.insert("v1", [1.0, 0.0, 0.0], {"label": "test"})
        vec = self.store.get("v1")
        assert vec is not None
        assert vec == [1.0, 0.0, 0.0]

    def test_similarity_search(self) -> None:
        self.store.insert("v1", [1.0, 0.0, 0.0])
        self.store.insert("v2", [0.0, 1.0, 0.0])
        results = self.store.similarity_search([1.0, 0.0, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0][0] == "v1"

    def test_delete(self) -> None:
        self.store.insert("v1", [1.0, 0.0, 0.0])
        assert self.store.delete("v1") is True
        assert self.store.get("v1") is None
        assert self.store.delete("nonexistent") is False

    def test_update(self) -> None:
        self.store.insert("v1", [1.0, 0.0, 0.0])
        assert self.store.update("v1", [0.0, 1.0, 0.0]) is True
        assert self.store.get("v1") == [0.0, 1.0, 0.0]
        assert self.store.update("nonexistent", [0.0, 0.0, 1.0]) is False

    def test_count_and_clear(self) -> None:
        assert self.store.count == 0
        self.store.insert("v1", [1.0, 0.0, 0.0])
        self.store.insert("v2", [0.0, 1.0, 0.0])
        assert self.store.count == 2
        self.store.clear()
        assert self.store.count == 0

    def test_batch_insert(self) -> None:
        items = [("a", [1.0, 0.0], {"i": 1}), ("b", [0.0, 1.0], {"i": 2})]
        self.store.batch_insert(items)
        assert self.store.count == 2

    def test_dimension_enforcement(self) -> None:
        self.store.insert("v1", [1.0, 0.0, 0.0])
        try:
            self.store.insert("v2", [1.0, 0.0])
            raise AssertionError("Should raise ValueError")
        except ValueError:
            pass

    def test_exists(self) -> None:
        self.store.insert("v1", [1.0, 0.0, 0.0])
        assert self.store.exists("v1") is True
        assert self.store.exists("nonexistent") is False

    def test_get_metadata(self) -> None:
        self.store.insert("v1", [1.0, 0.0, 0.0], {"key": "val"})
        assert self.store.get_metadata("v1") == {"key": "val"}
        assert self.store.get_metadata("nonexistent") == {}

    def test_vector_ids(self) -> None:
        self.store.insert("a", [1.0, 0.0])
        self.store.insert("b", [0.0, 1.0])
        assert set(self.store.vector_ids) == {"a", "b"}


class TestSimilarityEngine:
    def setup_method(self) -> None:
        self.engine = SimilarityEngine()

    def test_cosine_similarity_identical(self) -> None:
        sim = self.engine.cosine_similarity([1.0, 0.0, 0.0], [1.0, 0.0, 0.0])
        assert abs(sim - 1.0) < 1e-9

    def test_cosine_similarity_orthogonal(self) -> None:
        sim = self.engine.cosine_similarity([1.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        assert abs(sim - 0.0) < 1e-9

    def test_euclidean_similarity(self) -> None:
        sim = self.engine.euclidean_similarity([0.0, 0.0], [1.0, 1.0])
        assert 0.0 < sim < 1.0

    def test_dot_product(self) -> None:
        dot = self.engine.dot_product([1.0, 0.0], [2.0, 3.0])
        assert dot == 2.0

    def test_manhattan_similarity(self) -> None:
        sim = self.engine.manhattan_similarity([0.0, 0.0], [1.0, 1.0])
        assert 0.0 < sim < 1.0

    def test_compare_cosine(self) -> None:
        sim = self.engine.compare([1.0, 0.0], [1.0, 0.0], "cosine")
        assert abs(sim - 1.0) < 1e-9

    def test_compare_unknown_metric(self) -> None:
        try:
            self.engine.compare([1.0, 0.0], [0.0, 1.0], "unknown")
            raise AssertionError("Should raise ValueError")
        except ValueError:
            pass

    def test_dimension_mismatch(self) -> None:
        try:
            self.engine.cosine_similarity([1.0], [1.0, 0.0])
            raise AssertionError("Should raise ValueError")
        except ValueError:
            pass


class TestEmbeddingRepository:
    def setup_method(self) -> None:
        self.repo = EmbeddingRepository()

    def test_store_and_get(self) -> None:
        self.repo.store("v1", [1.0, 0.0], {"label": "x"})
        entry = self.repo.get("v1")
        assert entry is not None
        assert entry.vector_id == "v1"
        assert entry.vector == [1.0, 0.0]

    def test_count(self) -> None:
        assert self.repo.count == 0
        self.repo.store("a", [1.0], {})
        assert self.repo.count == 1

    def test_remove(self) -> None:
        self.repo.store("a", [1.0], {})
        assert self.repo.remove("a") is True
        assert self.repo.remove("nonexistent") is False

    def test_update(self) -> None:
        self.repo.store("a", [1.0], {})
        assert self.repo.update("a", [2.0], {}) is True
        assert self.repo.update("nonexistent", [1.0], {}) is False

    def test_search_by_metadata(self) -> None:
        self.repo.store("a", [1.0], {"type": "x"})
        self.repo.store("b", [2.0], {"type": "y"})
        results = self.repo.search_by_metadata("type", "x")
        assert len(results) == 1
        assert results[0].vector_id == "a"

    def test_list_ids(self) -> None:
        self.repo.store("a", [1.0], {})
        self.repo.store("b", [2.0], {})
        assert set(self.repo.list_ids()) == {"a", "b"}

    def test_clear(self) -> None:
        self.repo.store("a", [1.0], {})
        self.repo.clear()
        assert self.repo.count == 0


class TestReranker:
    def setup_method(self) -> None:
        self.reranker = Reranker()

    def test_rerank_empty(self) -> None:
        assert self.reranker.rerank([1.0, 0.0], []) == []


class TestRetrievalEngine:
    def setup_method(self) -> None:
        store = VectorStore()
        store.insert("v1", [1.0, 0.0, 0.0], {"relevance": 0.9})
        store.insert("v2", [0.0, 1.0, 0.0], {"relevance": 0.5})
        self.engine = RetrievalEngine(store)

    def test_retrieve_by_id(self) -> None:
        result = self.engine.retrieve_by_id("v1")
        assert result is not None
        assert result.vector_id == "v1"

    def test_retrieve_by_id_nonexistent(self) -> None:
        assert self.engine.retrieve_by_id("nonexistent") is None


class TestEmbeddingManager:
    def setup_method(self) -> None:
        self.manager = EmbeddingManager()

    def test_embed(self) -> None:
        vec = self.manager.embed("hello world")
        assert len(vec) > 0
        assert all(isinstance(v, float) for v in vec)

    def test_embed_caching(self) -> None:
        v1 = self.manager.embed("test content")
        v2 = self.manager.embed("test content")
        assert v1 == v2


class TestStatistics:
    def setup_method(self) -> None:
        self.stats = Statistics()

    def test_initial_state(self) -> None:
        s = self.stats.snapshot()
        assert s["total_queries"] == 0
        assert s["avg_query_time"] == 0.0

    def test_record_query(self) -> None:
        self.stats.record_query(0.5)
        assert self.stats.total_queries == 1
        assert self.stats.avg_query_time == 0.5

    def test_cache_hit_rate(self) -> None:
        assert self.stats.cache_hit_rate == 0.0
        self.stats.record_cache_hit()
        self.stats.record_cache_hit()
        self.stats.record_cache_miss()
        rate = self.stats.cache_hit_rate
        assert abs(rate - 2.0 / 3.0) < 1e-9

    def test_reset(self) -> None:
        self.stats.record_query(0.5)
        self.stats.reset()
        assert self.stats.total_queries == 0
        assert self.stats.avg_query_time == 0.0


class TestOptimizer:
    def setup_method(self) -> None:
        store = VectorStore()
        store.insert("v1", [1.0, 0.0, 0.0], {"importance": 0.05})
        store.insert("v2", [0.0, 1.0, 0.0], {"importance": 0.5})
        self.optimizer = Optimizer(store)

    def test_prune_low_importance(self) -> None:
        removed = self.optimizer.prune_low_importance(0.1)
        assert removed >= 1

    def test_stats(self) -> None:
        s = self.optimizer.stats()
        assert s["optimization_count"] == 0
        assert s["vector_count"] == 2


class TestBackup:
    def setup_method(self) -> None:
        repo = EmbeddingRepository()
        repo.store("a", [1.0, 0.0], {"key": "val"})
        self.backup = Backup(repo)

    def test_create_and_get_backup(self) -> None:
        bid = self.backup.create_backup("test_bk")
        entries = self.backup.get_backup(bid)
        assert entries is not None
        assert len(entries) == 1
        assert entries[0].vector_id == "a"

    def test_list_backups(self) -> None:
        self.backup.create_backup("b1")
        self.backup.create_backup("b2")
        assert len(self.backup.list_backups()) == 2

    def test_delete_backup(self) -> None:
        self.backup.create_backup("b1")
        assert self.backup.delete_backup("b1") is True
        assert self.backup.delete_backup("nonexistent") is False


class TestRestore:
    def setup_method(self) -> None:
        repo = EmbeddingRepository()
        repo.store("a", [1.0, 0.0], {"key": "val"})
        backup = Backup(repo)
        backup.create_backup("bk1")
        self.restore = Restore(repo, backup)

    def test_restore_from_backup(self) -> None:
        count = self.restore.restore_from_backup("bk1")
        assert count == 1


class TestCache:
    def setup_method(self) -> None:
        self.cache = Cache(max_size=10)

    def test_set_and_get(self) -> None:
        self.cache.set("key1", [1.0, 0.0, 0.0])
        val = self.cache.get("key1")
        assert val == [1.0, 0.0, 0.0]

    def test_get_miss(self) -> None:
        assert self.cache.get("nonexistent") is None

    def test_hit_rate(self) -> None:
        self.cache.get("a")
        self.cache.set("b", [1.0])
        self.cache.get("b")
        assert self.cache.hit_rate == 0.5

    def test_remove(self) -> None:
        self.cache.set("k", [1.0])
        assert self.cache.remove("k") is True
        assert self.cache.remove("k") is False

    def test_clear(self) -> None:
        self.cache.set("k", [1.0])
        self.cache.clear()
        assert self.cache.size == 0

    def test_max_size_eviction(self) -> None:
        small = Cache(max_size=2)
        small.set("a", [1.0])
        small.set("b", [2.0])
        small.set("c", [3.0])
        assert small.size <= 2
