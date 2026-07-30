from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Protocol, runtime_checkable


@runtime_checkable
class StreamableProtocol(Protocol):
    async def stream(self) -> AsyncIterator[dict[str, Any]]: ...


@runtime_checkable
class CacheableProtocol(Protocol):
    def cache_key(self) -> str: ...
    def cache_ttl(self) -> int: ...


@runtime_checkable
class RateLimitableProtocol(Protocol):
    def rate_limit_key(self) -> str: ...
    def rate_limit_max(self) -> int: ...


@runtime_checkable
class ValidatableProtocol(Protocol):
    async def validate(self) -> dict[str, Any]: ...


@runtime_checkable
class SerializableProtocol(Protocol):
    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class AuthenticatedProtocol(Protocol):
    user_id: str
    permissions: list[str]


class APIEvent(ABC):
    @abstractmethod
    def event_type(self) -> str: ...
    @abstractmethod
    def to_payload(self) -> dict[str, Any]: ...


class APIInterceptor(ABC):
    @abstractmethod
    async def intercept(self, request: Any, response: Any) -> Any: ...
