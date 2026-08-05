"""AIOS Runtime — base runtime abstraction.

A runtime provides an isolated execution environment for a unit of
work (task, agent, workflow, plugin...). This module defines the
abstract contract and a registry that maps runtime kinds to
implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable

RuntimeCallable = Callable[[dict[str, Any]], Awaitable[dict[str, Any]] | dict[str, Any]]


class BaseRuntime(ABC):
    """Contract every runtime implementation must satisfy."""

    kind: str = "base"

    def __init__(self, name: str, limits: dict[str, Any] | None = None) -> None:
        self.name = name
        self.limits = limits or {}

    @abstractmethod
    async def run(self, target: RuntimeCallable, context: dict[str, Any]) -> dict[str, Any]:
        """Execute ``target`` inside this runtime with ``context``."""


class RuntimeRegistry:
    """Maps runtime kinds to concrete runtime classes."""

    def __init__(self) -> None:
        self._runtimes: dict[str, BaseRuntime] = {}

    def register(self, runtime: BaseRuntime) -> "RuntimeRegistry":
        self._runtimes[runtime.kind] = runtime
        return self

    def get(self, kind: str, default: Any = None) -> BaseRuntime | None:
        return self._runtimes.get(kind, default)

    def kinds(self) -> list[str]:
        return sorted(self._runtimes)

    def snapshot(self) -> dict[str, Any]:
        return {
            "kinds": self.kinds(),
            "runtimes": {k: r.name for k, r in sorted(self._runtimes.items())},
        }
