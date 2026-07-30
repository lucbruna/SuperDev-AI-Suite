from __future__ import annotations

from typing import Any, AsyncIterator, Protocol, runtime_checkable


@runtime_checkable
class StreamableProvider(Protocol):
    """Protocol for providers that support streaming."""

    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]: ...


@runtime_checkable
class FunctionCallProvider(Protocol):
    """Protocol for providers that support function/tool calling."""

    async def generate_with_functions(
        self, prompt: str, functions: list[dict[str, Any]], **kwargs: Any
    ) -> dict[str, Any]: ...


@runtime_checkable
class VisionProvider(Protocol):
    """Protocol for providers that support vision/image inputs."""

    async def generate_with_vision(
        self, prompt: str, images: list[bytes], **kwargs: Any
    ) -> dict[str, Any]: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    """Protocol for providers that support embeddings."""

    async def embed(self, texts: list[str], **kwargs: Any) -> list[list[float]]: ...


@runtime_checkable
class CacheableProvider(Protocol):
    """Protocol for providers that support caching."""

    async def cache_key(self, prompt: str, **kwargs: Any) -> str: ...


@runtime_checkable
class RoutableProvider(Protocol):
    """Protocol for providers that expose routing metadata."""

    @property
    def capabilities(self) -> list[str]: ...

    @property
    def estimated_cost(self) -> float: ...

    @property
    def estimated_latency(self) -> float: ...
