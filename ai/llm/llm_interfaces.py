from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class ILLMProvider(ABC):
    """Interface that all LLM providers must implement."""

    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def model(self) -> str:
        ...

    @abstractmethod
    async def generate(self, prompt: str, **kwargs: Any) -> dict[str, Any]:
        ...

    @abstractmethod
    async def generate_stream(self, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        ...

    @abstractmethod
    async def validate(self, params: dict[str, Any]) -> bool:
        ...

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass


class ILLMRegistry(ABC):
    """Interface for LLM provider registration and discovery."""

    @abstractmethod
    def register(self, provider: ILLMProvider) -> str:
        ...

    @abstractmethod
    def unregister(self, name: str) -> bool:
        ...

    @abstractmethod
    def get(self, name: str) -> ILLMProvider | None:
        ...

    @abstractmethod
    def list_providers(self) -> list[ILLMProvider]:
        ...


class ILLMFactory(ABC):
    """Interface for creating LLM provider instances."""

    @abstractmethod
    def create(self, provider_type: str, **kwargs: Any) -> ILLMProvider:
        ...


class ILLMExecutor(ABC):
    """Interface for LLM execution."""

    @abstractmethod
    async def execute(self, provider: str, prompt: str, **kwargs: Any) -> dict[str, Any]:
        ...

    @abstractmethod
    async def execute_stream(self, provider: str, prompt: str, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        ...


class ILLMRouter(ABC):
    """Interface for LLM routing decisions."""

    @abstractmethod
    async def select(self, prompt: str, **kwargs: Any) -> str:
        ...


class ILLMCache(ABC):
    """Interface for LLM response caching."""

    @abstractmethod
    async def get(self, key: str) -> dict[str, Any] | None:
        ...

    @abstractmethod
    async def set(self, key: str, value: dict[str, Any], ttl: int = 300) -> None:
        ...

    @abstractmethod
    async def invalidate(self, key: str) -> bool:
        ...


class ILLMContext(ABC):
    """Interface for LLM context management."""

    @abstractmethod
    def build(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        ...

    @abstractmethod
    def truncate(self, context: dict[str, Any], max_tokens: int) -> dict[str, Any]:
        ...


class ILLMSecurity(ABC):
    """Interface for LLM security and moderation."""

    @abstractmethod
    async def validate_prompt(self, prompt: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def validate_output(self, output: str) -> dict[str, Any]:
        ...
