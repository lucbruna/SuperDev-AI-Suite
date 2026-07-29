import pytest
import math
from ..embedding_engine import EmbeddingEngine, EmbeddingConfig
from ..model_manager import ModelManager
from ..encoder import Encoder
from ..similarity import SimilarityCalculator


class TestEmbeddingEngine:
    @pytest.fixture
    async def engine(self):
        eng = EmbeddingEngine(EmbeddingConfig(embedding_dim=8))
        await eng.initialize()
        yield eng
        await eng.stop()

    def test_initial_state(self, engine):
        assert engine.state.initialized is True
        assert engine.state.model_loaded is True

    def test_encode(self, engine):
        vec = asyncio_run(engine.encode("hello world"))
        assert len(vec) == 8
        norm = math.sqrt(sum(v * v for v in vec))
        assert abs(norm - 1.0) < 0.001

    def test_encode_deterministic(self, engine):
        v1 = asyncio_run(engine.encode("same text"))
        v2 = asyncio_run(engine.encode("same text"))
        assert v1 == v2

    def test_encode_batch(self, engine):
        texts = ["hello", "world", "test"]
        results = asyncio_run(engine.encode_batch(texts))
        assert len(results) == 3
        assert all(len(v) == 8 for v in results)

    def test_get_embedding_size(self, engine):
        assert asyncio_run(engine.get_embedding_size()) == 8

    def test_get_model_info(self, engine):
        info = asyncio_run(engine.get_model_info())
        assert info["model_name"] == "mock-bert-base"
        assert info["embedding_dim"] == 8


class TestModelManager:
    def test_load_and_list(self):
        mgr = ModelManager()
        info = mgr.load_model("bert-base", 128, "transformer")
        assert mgr.get_active_model().name == "bert-base"
        models = mgr.list_models()
        assert len(models) == 1

    def test_unload_model(self):
        mgr = ModelManager()
        info = mgr.load_model("test-model")
        assert mgr.unload_model(info.model_id) is True
        assert mgr.get_active_model() is None
        assert mgr.unload_model("bad") is False

    def test_switch_model(self):
        mgr = ModelManager()
        m1 = mgr.load_model("model-a")
        m2 = mgr.load_model("model-b")
        assert mgr.get_active_model().model_id == m2.model_id
        assert mgr.switch_model(m1.model_id) is True
        assert mgr.get_active_model().model_id == m1.model_id
        assert mgr.switch_model("bad") is False

    def test_get_model_info(self):
        mgr = ModelManager()
        m = mgr.load_model("my-model")
        info = mgr.get_model_info(m.model_id)
        assert info is not None
        assert info.name == "my-model"
        assert mgr.get_model_info("nonexistent") is None


class TestEncoder:
    def test_encode_text(self):
        enc = Encoder(embedding_dim=16)
        vec = enc.encode_text("hello world")
        assert len(vec) == 16
        stats = enc.get_encoding_stats()
        assert stats.total_encoded == 1

    def test_encode_document(self):
        enc = Encoder(8)
        vec = enc.encode_document("doc content", {"title": "Test Doc"})
        assert len(vec) == 8

    def test_encode_query(self):
        enc = Encoder(8)
        vec = enc.encode_query("search query")
        assert len(vec) == 8

    def test_batch_encode(self):
        enc = Encoder(4)
        results = enc.batch_encode(["a", "b", "c"])
        assert len(results) == 3
        assert all(len(v) == 4 for v in results)

    def test_get_encoding_stats(self):
        enc = Encoder(8)
        enc.encode_text("first")
        enc.encode_text("second")
        stats = enc.get_encoding_stats()
        assert stats.total_encoded == 2
        assert stats.embedding_dim == 8


class TestSimilarityCalculator:
    def test_cosine_similarity(self):
        sc = SimilarityCalculator()
        score = sc.cosine_similarity([1.0, 0.0], [0.0, 1.0])
        assert abs(score) < 0.001
        score2 = sc.cosine_similarity([1.0, 0.0], [1.0, 0.0])
        assert abs(score2 - 1.0) < 0.001

    def test_dot_product(self):
        sc = SimilarityCalculator()
        dp = sc.dot_product([1.0, 2.0], [3.0, 4.0])
        assert abs(dp - 11.0) < 0.001

    def test_euclidean_distance(self):
        sc = SimilarityCalculator()
        d = sc.euclidean_distance([0.0, 0.0], [3.0, 4.0])
        assert abs(d - 5.0) < 0.001

    def test_rank_by_similarity(self):
        sc = SimilarityCalculator()
        vectors = {
            "a": [1.0, 0.0],
            "b": [0.0, 1.0],
            "c": [0.707, 0.707],
        }
        results = sc.rank_by_similarity([1.0, 0.0], vectors)
        assert len(results) == 3
        assert results[0].id == "a"
        assert results[-1].id == "b"

    def test_get_most_similar(self):
        sc = SimilarityCalculator()
        vectors = {"x": [1.0, 0.0], "y": [0.0, 1.0]}
        results = sc.get_most_similar([1.0, 0.0], vectors, n=1)
        assert len(results) == 1
        assert results[0].id == "x"


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
