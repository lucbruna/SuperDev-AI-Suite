from __future__ import annotations

import math
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class EngineConfig:
    dimension: int = 128
    index_type: str = "flat"
    similarity_metric: str = "cosine"
    max_memory_mb: int = 512
    auto_optimize: bool = True


@dataclass
class EngineState:
    initialized: bool = False
    index_count: int = 0
    vector_count: int = 0
    memory_usage_mb: float = 0.0
    last_optimized: Optional[float] = None


@dataclass
class EngineMetrics:
    total_indexed: int = 0
    total_searched: int = 0
    total_stored: int = 0
    total_deleted: int = 0
    avg_index_time_ms: float = 0.0
    avg_search_time_ms: float = 0.0
    errors: int = 0


class VectorEngine:
    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState()
        self.metrics = EngineMetrics()
        self._vectors: dict[str, list[float]] = {}
        self._metadata: dict[str, dict[str, Any]] = {}
        self._indexes: dict[str, list[str]] = {}

    async def initialize(self) -> None:
        self.state.initialized = True
        self.state.index_count = 0
        self.state.vector_count = 0
        self.state.memory_usage_mb = 0.0

    async def stop(self) -> None:
        self._vectors.clear()
        self._metadata.clear()
        self._indexes.clear()
        self.state.initialized = False
        self.state.vector_count = 0
        self.state.index_count = 0

    async def index(self, vectors: list[list[float]], metadata: Optional[list[dict[str, Any]]] = None) -> list[str]:
        start = time.perf_counter()
        ids: list[str] = []
        for i, vec in enumerate(vectors):
            vid = str(uuid.uuid4())
            self._vectors[vid] = vec
            self._metadata[vid] = (metadata or [{}])[i] if metadata else {}
            ids.append(vid)
        self.state.vector_count = len(self._vectors)
        self.state.memory_usage_mb = self._estimate_memory()
        elapsed = (time.perf_counter() - start) * 1000
        n = len(vectors)
        self.metrics.total_indexed += n
        self.metrics.avg_index_time_ms = (
            (self.metrics.avg_index_time_ms * (self.metrics.total_indexed - n) + elapsed) / self.metrics.total_indexed
            if self.metrics.total_indexed else elapsed
        )
        return ids

    async def search(self, query_vector: list[float], top_k: int = 10) -> list[tuple[str, float]]:
        start = time.perf_counter()
        if not self._vectors:
            self.metrics.total_searched += 1
            return []
        scored: list[tuple[str, float]] = []
        for vid, vec in self._vectors.items():
            score = self._cosine_similarity(query_vector, vec)
            scored.append((vid, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        result = scored[:top_k]
        elapsed = (time.perf_counter() - start) * 1000
        self.metrics.total_searched += 1
        self.metrics.avg_search_time_ms = (
            (self.metrics.avg_search_time_ms * (self.metrics.total_searched - 1) + elapsed) / self.metrics.total_searched
        )
        return result

    async def store(self, vector: list[float], metadata: Optional[dict[str, Any]] = None) -> str:
        vid = str(uuid.uuid4())
        self._vectors[vid] = vector
        self._metadata[vid] = metadata or {}
        self.state.vector_count = len(self._vectors)
        self.state.memory_usage_mb = self._estimate_memory()
        self.metrics.total_stored += 1
        return vid

    async def delete(self, vector_id: str) -> bool:
        if vector_id in self._vectors:
            del self._vectors[vector_id]
            self._metadata.pop(vector_id, None)
            self.state.vector_count = len(self._vectors)
            self.state.memory_usage_mb = self._estimate_memory()
            self.metrics.total_deleted += 1
            return True
        self.metrics.errors += 1
        return False

    async def get_stats(self) -> dict[str, Any]:
        return {
            "config": {
                "dimension": self.config.dimension,
                "index_type": self.config.index_type,
                "similarity_metric": self.config.similarity_metric,
                "max_memory_mb": self.config.max_memory_mb,
                "auto_optimize": self.config.auto_optimize,
            },
            "state": {
                "initialized": self.state.initialized,
                "index_count": self.state.index_count,
                "vector_count": self.state.vector_count,
                "memory_usage_mb": round(self.state.memory_usage_mb, 2),
                "last_optimized": self.state.last_optimized,
            },
            "metrics": {
                "total_indexed": self.metrics.total_indexed,
                "total_searched": self.metrics.total_searched,
                "total_stored": self.metrics.total_stored,
                "total_deleted": self.metrics.total_deleted,
                "avg_index_time_ms": round(self.metrics.avg_index_time_ms, 4),
                "avg_search_time_ms": round(self.metrics.avg_search_time_ms, 4),
                "errors": self.metrics.errors,
            },
        }

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        dot = sum(ai * bi for ai, bi in zip(a, b))
        na = math.sqrt(sum(ai * ai for ai in a))
        nb = math.sqrt(sum(bi * bi for bi in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def _estimate_memory(self) -> float:
        vector_bytes = sum(len(v) * 8 for v in self._vectors.values())
        meta_bytes = sum(len(str(m)) for m in self._metadata.values())
        total_bytes = vector_bytes + meta_bytes
        return total_bytes / (1024 * 1024)
