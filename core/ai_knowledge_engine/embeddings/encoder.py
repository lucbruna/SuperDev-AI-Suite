from __future__ import annotations

import hashlib
import math
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EncodingStats:
    total_encoded: int = 0
    total_tokens: int = 0
    avg_encoding_time_ms: float = 0.0
    embedding_dim: int = 128


class Encoder:
    def __init__(self, embedding_dim: int = 128) -> None:
        self.embedding_dim = embedding_dim
        self.stats = EncodingStats(embedding_dim=embedding_dim)

    def encode_text(self, text: str) -> list[float]:
        start = time.perf_counter()
        vec = self._hash_to_vector(text)
        elapsed = (time.perf_counter() - start) * 1000
        self.stats.total_encoded += 1
        self.stats.total_tokens += len(text.split())
        n = self.stats.total_encoded
        self.stats.avg_encoding_time_ms = (
            (self.stats.avg_encoding_time_ms * (n - 1) + elapsed) / n
        )
        return vec

    def encode_document(self, document: str, metadata: Optional[dict] = None) -> list[float]:
        combined = document
        if metadata:
            for v in metadata.values():
                combined += str(v)
        return self.encode_text(combined)

    def encode_query(self, query: str) -> list[float]:
        return self.encode_text(query)

    def batch_encode(self, texts: list[str]) -> list[list[float]]:
        return [self.encode_text(t) for t in texts]

    def get_encoding_stats(self) -> EncodingStats:
        return self.stats

    def _hash_to_vector(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode()).hexdigest()
        seed = int(h[:16], 16)
        rng = _SimpleRNG(seed)
        dim = self.embedding_dim
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
