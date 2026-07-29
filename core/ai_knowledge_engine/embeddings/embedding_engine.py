from __future__ import annotations

import hashlib
import math
import time
import uuid
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class EmbeddingConfig:
    model_name: str = "mock-bert-base"
    embedding_dim: int = 128
    max_sequence_length: int = 512
    device: str = "cpu"
    batch_size: int = 32


@dataclass
class EmbeddingState:
    initialized: bool = False
    model_loaded: bool = False
    current_model: str = ""
    total_embeddings: int = 0
    memory_usage_mb: float = 0.0


@dataclass
class EmbeddingMetrics:
    total_encoded: int = 0
    total_batches: int = 0
    avg_encode_time_ms: float = 0.0
    avg_batch_time_ms: float = 0.0
    errors: int = 0


class EmbeddingEngine:
    def __init__(self, config: Optional[EmbeddingConfig] = None) -> None:
        self.config = config or EmbeddingConfig()
        self.state = EmbeddingState()
        self.metrics = EmbeddingMetrics()

    async def initialize(self) -> None:
        self.state.initialized = True
        self.state.model_loaded = True
        self.state.current_model = self.config.model_name

    async def stop(self) -> None:
        self.state.initialized = False
        self.state.model_loaded = False
        self.state.total_embeddings = 0

    async def encode(self, text: str) -> list[float]:
        start = time.perf_counter()
        vector = self._hash_to_vector(text)
        elapsed = (time.perf_counter() - start) * 1000
        self.state.total_embeddings += 1
        n = self.metrics.total_encoded + 1
        self.metrics.total_encoded = n
        self.metrics.avg_encode_time_ms = (
            (self.metrics.avg_encode_time_ms * (n - 1) + elapsed) / n
        )
        return vector

    async def encode_batch(self, texts: list[str]) -> list[list[float]]:
        start = time.perf_counter()
        results = [self._hash_to_vector(t) for t in texts]
        elapsed = (time.perf_counter() - start) * 1000
        self.state.total_embeddings += len(texts)
        self.metrics.total_encoded += len(texts)
        self.metrics.total_batches += 1
        nb = self.metrics.total_batches
        self.metrics.avg_batch_time_ms = (
            (self.metrics.avg_batch_time_ms * (nb - 1) + elapsed) / nb
        )
        return results

    async def get_embedding_size(self) -> int:
        return self.config.embedding_dim

    async def get_model_info(self) -> dict[str, Any]:
        return {
            "model_name": self.config.model_name,
            "embedding_dim": self.config.embedding_dim,
            "max_sequence_length": self.config.max_sequence_length,
            "device": self.config.device,
            "state": {
                "initialized": self.state.initialized,
                "model_loaded": self.state.model_loaded,
                "total_embeddings": self.state.total_embeddings,
                "memory_usage_mb": round(self.state.memory_usage_mb, 2),
            },
            "metrics": {
                "total_encoded": self.metrics.total_encoded,
                "total_batches": self.metrics.total_batches,
                "avg_encode_time_ms": round(self.metrics.avg_encode_time_ms, 4),
                "avg_batch_time_ms": round(self.metrics.avg_batch_time_ms, 4),
                "errors": self.metrics.errors,
            },
        }

    def _hash_to_vector(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode()).hexdigest()
        seed = int(h[:16], 16)
        rng = _SimpleRNG(seed)
        dim = self.config.embedding_dim
        vec = [rng.next() for _ in range(dim)]
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec


class _SimpleRNG:
    def __init__(self, seed: int) -> None:
        self._state = seed

    def next(self) -> float:
        self._state = (self._state * 1103515245 + 12345) & 0x7FFFFFFF
        return (self._state % 100000) / 100000.0
