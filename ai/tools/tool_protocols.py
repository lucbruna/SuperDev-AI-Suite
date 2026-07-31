from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ToolCapability(Protocol):
    """Protocol for tools that expose capabilities."""

    def capabilities(self) -> list[str]: ...


@runtime_checkable
class RollbackCapable(Protocol):
    """Protocol for tools that support rollback."""

    async def rollback(self) -> None: ...


@runtime_checkable
class CacheableTool(Protocol):
    """Protocol for tools that support caching."""

    def cache_key(self, params: dict[str, Any]) -> str: ...


class ToolHook(Protocol):
    """Protocol for tool lifecycle hooks."""

    async def __call__(self, tool_name: str, params: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]: ...
