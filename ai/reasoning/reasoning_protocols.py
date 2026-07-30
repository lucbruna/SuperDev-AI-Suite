from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ReasoningEngineProtocol(Protocol):
    """Protocol for reasoning engine implementations."""

    async def reason(self, context: Any) -> Any: ...


@runtime_checkable
class MemoryProtocol(Protocol):
    """Protocol for reasoning memory implementations."""

    async def store(self, key: str, value: Any) -> None: ...
    async def retrieve(self, key: str) -> Any: ...
    async def forget(self, key: str) -> bool: ...


@runtime_checkable
class EvaluatorProtocol(Protocol):
    """Protocol for hypothesis evaluation."""

    async def evaluate(self, hypothesis: str, context: Any) -> dict[str, Any]: ...
