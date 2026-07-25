from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ModelInfo:
    id: str
    name: str
    provider: str
    capabilities: list[str] = field(default_factory=list)
    context_window: int = 4096
    max_tokens: int = 2048


@dataclass
class Choice:
    index: int = 0
    message: dict[str, Any] = field(default_factory=dict)
    finish_reason: str = "stop"


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ChatResponse:
    id: str = ""
    model: str = ""
    choices: list[Choice] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)
    provider: str = ""
    raw: dict[str, Any] | None = None


@dataclass
class StreamChunk:
    delta: str = ""
    finish_reason: str | None = None
    usage: Usage | None = None
    index: int = 0
    model: str = ""


@dataclass
class HealthStatus:
    status: str = "unknown"
    latency_ms: float = 0.0
    last_check: datetime | None = None
    error: str | None = None


@dataclass
class ProviderLimits:
    max_requests_per_minute: int = 60
    max_tokens_per_minute: int = 100000
    max_concurrent_requests: int = 10


@dataclass
class PricingInfo:
    input_per_1k: float = 0.0
    output_per_1k: float = 0.0
    currency: str = "USD"


class BaseProvider(ABC):
    def __init__(self, config: Any):
        self.config = config
        self._client = None

    @abstractmethod
    async def authenticate(self) -> str:
        ...

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        ...

    @abstractmethod
    async def chat(self, messages: list[dict], config: dict[str, Any]) -> ChatResponse:
        ...

    @abstractmethod
    async def stream(self, messages: list[dict], config: dict[str, Any]) -> AsyncIterator[StreamChunk]:
        ...
        if False:
            yield

    @abstractmethod
    async def embeddings(self, texts: list[str]) -> list[list[float]]:
        ...

    async def vision(self, image: str, prompt: str) -> str:
        raise NotImplementedError(f"{type(self).__name__} does not support vision")

    @abstractmethod
    async def health(self) -> HealthStatus:
        ...

    @abstractmethod
    async def limits(self) -> ProviderLimits:
        ...

    @abstractmethod
    async def pricing(self) -> PricingInfo:
        ...
