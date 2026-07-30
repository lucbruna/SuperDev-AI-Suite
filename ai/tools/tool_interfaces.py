from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ITool(ABC):
    """Interface that all tools must implement."""

    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def description(self) -> str:
        ...

    @abstractmethod
    def permissions(self) -> list[str]:
        ...

    @abstractmethod
    async def validate(self, params: dict[str, Any]) -> bool:
        ...

    @abstractmethod
    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        ...

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass


class IToolRegistry(ABC):
    """Interface for tool registration and discovery."""

    @abstractmethod
    def register(self, tool: ITool) -> str:
        ...

    @abstractmethod
    def unregister(self, name: str) -> bool:
        ...

    @abstractmethod
    def get(self, name: str) -> ITool | None:
        ...

    @abstractmethod
    def list_tools(self) -> list[ITool]:
        ...


class IToolExecutor(ABC):
    """Interface for tool execution."""

    @abstractmethod
    async def execute(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    async def validate(self, tool_name: str, params: dict[str, Any]) -> bool:
        ...


class IToolFactory(ABC):
    """Interface for creating tool instances."""

    @abstractmethod
    def create(self, tool_type: str, **kwargs: Any) -> ITool:
        ...
