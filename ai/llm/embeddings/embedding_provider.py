from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class EmbeddingProviderInterface(ABC):
    """Interface for embedding providers."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]: ...

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def dimensions(self) -> int: ...

    def to_dict(self) -> dict[str, Any]:
        return {"dimensions": self.dimensions()}


class MockEmbeddingProvider(EmbeddingProviderInterface):
    """Mock embedding provider for testing."""

    def __init__(self, dims: int = 384) -> None:
        self._dims = dims

    async def embed(self, text: str) -> list[float]:
        import hashlib

        h = hashlib.sha256(text.encode()).hexdigest()
        seed = int(h[:8], 16)
        rng = _SimpleRNG(seed)
        vec = [rng.random() for _ in range(self._dims)]
        norm = sum(x * x for x in vec) ** 0.5
        return [x / norm for x in vec]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [await self.embed(t) for t in texts]

    def dimensions(self) -> int:
        return self._dims

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["type"] = "mock"
        return base


class _SimpleRNG:
    """Simple seeded pseudo-random number generator."""

    def __init__(self, seed: int) -> None:
        self._state = seed

    def random(self) -> float:
        self._state = (self._state * 1103515245 + 12345) & 0x7FFFFFFF
        return self._state / 0x7FFFFFFF
