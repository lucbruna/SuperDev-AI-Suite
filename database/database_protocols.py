from __future__ import annotations

from typing import Any, AsyncIterator, Protocol, runtime_checkable


@runtime_checkable
class ConnectableProtocol(Protocol):
    """Protocol for objects that can connect/disconnect."""

    async def connect(self) -> None:
        ...

    async def disconnect(self) -> None:
        ...

    @property
    def is_connected(self) -> bool:
        ...


@runtime_checkable
class ExecutableProtocol(Protocol):
    """Protocol for objects that can execute queries."""

    async def execute(self, query: str, params: list[Any] | None = None) -> Any:
        ...

    async def execute_query(self, query: str, params: list[Any] | None = None) -> list[dict[str, Any]]:
        ...


@runtime_checkable
class TransactableProtocol(Protocol):
    """Protocol for objects supporting transactions."""

    async def begin(self) -> None:
        ...

    async def commit(self) -> None:
        ...

    async def rollback(self) -> None:
        ...


@runtime_checkable
class PoolableProtocol(Protocol):
    """Protocol for connection pool objects."""

    async def acquire(self) -> Any:
        ...

    async def release(self, conn: Any) -> None:
        ...

    async def close(self) -> None:
        ...


@runtime_checkable
class CachableProtocol(Protocol):
    """Protocol for cache objects."""

    async def get(self, key: str) -> Any:
        ...

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        ...

    async def delete(self, key: str) -> bool:
        ...


@runtime_checkable
class MigratableProtocol(Protocol):
    """Protocol for migration-supporting objects."""

    async def migrate(self, target: str | None = None) -> list[Any]:
        ...

    async def rollback(self, steps: int = 1) -> list[Any]:
        ...


@runtime_checkable
class HealthCheckableProtocol(Protocol):
    """Protocol for health-checkable objects."""

    async def ping(self) -> bool:
        ...

    async def health(self) -> dict[str, Any]:
        ...


@runtime_checkable
class SerializableProtocol(Protocol):
    """Protocol for serializable objects."""

    def to_dict(self) -> dict[str, Any]:
        ...

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Any:
        ...


@runtime_checkable
class AsyncIterableProtocol(Protocol):
    """Protocol for async-iterable query results."""

    def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        ...
