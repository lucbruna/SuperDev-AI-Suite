"""Tests for the knowledge embeddings subsystem."""

from __future__ import annotations

import pytest

from knowledge.embeddings import (
    Compression,
    EmbeddingEngine,
    EmbeddingMetadata,
    HashEmbeddingGenerator,
    ModelManager,
    SentenceChunker,
    SentenceChunker as _Sc,
    Similarity,
    SlidingWindowChunker,
    Tokenizer,
)


class TestSimilarity:
    def test_cosine(self) -> None:
        assert Similarity.cosine([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)
        assert Similarity.cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)
        assert Similarity.cosine([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)

    def test_cosine_mismatched_dimensions(self) -> None:
        assert Similarity.cosine([1.0], []) == 0.0
        assert Similarity.cosine([1.0, 2.0], [1.0]) == 0.0

    def test_dot_and_euclidean(self) -> None:
        assert Similarity.dot_product([1.0, 2.0], [3.0, 4.0]) == pytest.approx(11.0)
        assert Similarity.euclidean([0.0, 0.0], [3.0, 4.0]) == pytest.approx(5.0)
        assert Similarity.euclidean([1.0], [1.0, 2.0]) == float("inf")

    def test_jaccard(self) -> None:
        assert Similarity.jaccard({"a", "b"}, {"b", "c"}) == pytest.approx(1 / 3)
        assert Similarity.jaccard(set(), set()) == 0.0


class TestTokenizer:
    def test_tokenize_normalizes(self) -> None:
        tokenizer = Tokenizer()
        assert tokenizer.tokenize("Hello, WORLD_123!") == ["hello", "world_123"]

    def test_vocabulary(self) -> None:
        tokenizer = Tokenizer()
        vocabulary = tokenizer.vocabulary(["a b", "a c"])
        assert vocabulary == {"a": 2, "b": 1, "c": 1}

    def test_bag_of_words(self) -> None:
        tokenizer = Tokenizer()
        assert tokenizer.bag_of_words("a b a") == {"a": 2, "b": 1}
        assert tokenizer.bag_of_words("a", {"a": 0, "z": 0}) == {"a": 1, "z": 0}


class TestHashEmbeddingGenerator:
    def test_dimensions(self) -> None:
        generator = HashEmbeddingGenerator(dimensions=64)
        assert generator.dimensions() == 64

    def test_embed_length_and_determinism(self) -> None:
        generator = HashEmbeddingGenerator(dimensions=64)
        vector = generator.embed("hello world")
        assert len(vector) == 64
        assert vector == generator.embed("hello world")

    def test_similarity_between_overlapping_texts(self) -> None:
        generator = HashEmbeddingGenerator(dimensions=256)
        left = generator.embed("busca vetorial embeddings")
        right = generator.embed("busca vetorial")
        assert Similarity.cosine(left, right) > 0.0

    def test_empty_text_returns_zero_vector(self) -> None:
        generator = HashEmbeddingGenerator(dimensions=64)
        assert generator.embed("") == [0.0] * 64


class TestChunkers:
    def test_sliding_window(self) -> None:
        chunker = SlidingWindowChunker(chunk_size=10, overlap=2)
        chunks = chunker.chunk("abcdefghijklmnopqrstuvwxyz", "doc-1")
        assert len(chunks) >= 2
        assert chunks[0].document_id == "doc-1"
        assert chunks[0].index == 0

    def test_sliding_window_small_text(self) -> None:
        chunker = SlidingWindowChunker(chunk_size=50, overlap=4)
        chunks = chunker.chunk("short text", "doc-2")
        assert len(chunks) == 1
        assert chunks[0].text == "short text"

    def test_sentence_chunker(self) -> None:
        chunker = SentenceChunker(max_size=30)
        text = "First sentence is here. Second sentence is here too."
        chunks = chunker.chunk(text)
        assert len(chunks) >= 1
        assert all(chunk.text for chunk in chunks)


class TestModelManager:
    def test_default_provider(self) -> None:
        manager = ModelManager()
        assert manager.models() == ["local-hash"]
        provider = manager.get()
        assert provider.dimensions() == 384

    def test_unknown_model_raises(self) -> None:
        manager = ModelManager()
        with pytest.raises(KeyError):
            manager.get("missing")

    def test_register_custom(self) -> None:
        manager = ModelManager()
        custom = HashEmbeddingGenerator(dimensions=16)
        manager.register("mini", custom)
        assert manager.get("mini") is custom
        assert manager.status()["default"] == "local-hash"


class TestEmbeddingMetadata:
    def test_build(self) -> None:
        metadata = EmbeddingMetadata()
        result = metadata.build(document_id="doc-1", source="test")
        assert result["source"] == "test"
        assert result["document_id"] == "doc-1"

    def test_validate(self) -> None:
        metadata = EmbeddingMetadata()
        assert metadata.validate({"k": "v"}) is True
        assert metadata.validate({"k": object()}) is False

    def test_merge(self) -> None:
        metadata = EmbeddingMetadata()
        merged = metadata.merge({"a": 1}, {"b": 2, "a": 3})
        assert merged == {"a": 3, "b": 2}


class TestCompression:
    def test_quantize(self) -> None:
        compression = Compression()
        values = [1.0, 0.0, -0.5]
        quantized = compression.quantize(values, bits=8)
        assert quantized[0] == pytest.approx(1.0)
        assert quantized[1] == 0.0
        assert all(-1.0 <= v <= 1.0 for v in quantized)

    def test_truncate(self) -> None:
        compression = Compression()
        truncated = compression.truncate([1.0, 2.0, 3.0], keep=2)
        assert len(truncated) == 2

    def test_sparsity(self) -> None:
        assert Compression.sparsity([1.0, 0.0, 2.0]) == pytest.approx(2 / 3)
        assert Compression.sparsity([]) == 0.0


class TestEmbeddingEngine:
    def test_embed(self) -> None:
        engine = EmbeddingEngine()
        vector = engine.embed("engine embedding")
        assert len(vector) == 384

    def test_split_and_embed(self) -> None:
        engine = EmbeddingEngine()
        embeddings = engine.split_and_embed("A sentence about retrieval. Another sentence here.", "doc-9")
        assert len(embeddings) >= 1
        assert embeddings[0].document_id == "doc-9"
        assert len(embeddings[0].vector) == 384

    def test_chunk_text(self) -> None:
        engine = EmbeddingEngine()
        chunks = engine.chunk_text("x" * 2000, "doc-1")
        assert len(chunks) >= 2

    def test_status(self) -> None:
        engine = EmbeddingEngine()
        status = engine.status()
        assert status["chunk_size"] == 512
        assert status["models"]["default"] == "local-hash"
