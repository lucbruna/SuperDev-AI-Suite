from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any


@dataclass
class Message:
    role: str
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] | None = None


@dataclass
class CompletionResponse:
    id: str
    model: str
    content: str
    finish_reason: str | None = None
    usage: TokenUsage | None = None
    tool_calls: list[dict[str, Any]] | None = None


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0


@dataclass
class EmbeddingResponse:
    embeddings: list[list[float]]
    model: str
    usage: TokenUsage | None = None


@dataclass
class StreamChunk:
    id: str
    model: str
    delta: str
    finish_reason: str | None = None
    usage: TokenUsage | None = None


class BaseProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None, **kwargs):
        self.api_key = api_key
        self.base_url = base_url
        self.config = kwargs

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def supported_models(self) -> list[str]:
        ...

    @abstractmethod
    async def complete(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> CompletionResponse:
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[Message],
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        **kwargs,
    ) -> AsyncIterator[StreamChunk]:
        ...

    @abstractmethod
    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> EmbeddingResponse:
        ...

    async def health_check(self) -> bool:
        try:
            await self.complete(
                messages=[Message(role="user", content="ping")],
                model=self.supported_models[0],
                max_tokens=1,
            )
            return True
        except Exception:
            return False

    async def close(self) -> None:
        pass
