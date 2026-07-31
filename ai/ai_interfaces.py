from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any


class IAEngineInterface(ABC):
    """Public interface for the AI Engine."""

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the AI engine and all subsystems."""

    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the AI engine gracefully."""

    @abstractmethod
    async def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        """Send a chat completion."""

    @abstractmethod
    async def stream(self, messages: list[dict[str, Any]], **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        """Stream a chat completion."""

    @abstractmethod
    async def embeddings(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        """Generate embeddings."""

    @abstractmethod
    def health(self) -> dict[str, Any]:
        """Get engine health status."""


class IAManagerInterface(ABC):
    """Public interface for AI module management."""

    @abstractmethod
    def register_module(self, name: str, module: Any) -> None:
        """Register a sub-module."""

    @abstractmethod
    def unregister_module(self, name: str) -> None:
        """Unregister a sub-module."""

    @abstractmethod
    def get_module(self, name: str) -> Any | None:
        """Get a registered module by name."""

    @abstractmethod
    def list_modules(self) -> dict[str, str]:
        """List all registered modules with their types."""

    @abstractmethod
    def health(self) -> dict[str, Any]:
        """Get health status of all modules."""


class AIRegistryInterface(ABC):
    """Public interface for AI registry."""

    @abstractmethod
    def register_agent(self, name: str, agent: Any) -> None:
        """Register an agent."""

    @abstractmethod
    def register_tool(self, name: str, tool: Any) -> None:
        """Register a tool."""

    @abstractmethod
    def register_model(self, name: str, model_config: dict[str, Any]) -> None:
        """Register a model configuration."""

    @abstractmethod
    def get_agent(self, name: str) -> Any | None:
        """Get a registered agent."""

    @abstractmethod
    def get_tool(self, name: str) -> Any | None:
        """Get a registered tool."""

    @abstractmethod
    def list_agents(self) -> list[str]:
        """List all registered agents."""

    @abstractmethod
    def list_tools(self) -> list[str]:
        """List all registered tools."""

    @abstractmethod
    def list_models(self) -> list[dict[str, Any]]:
        """List all registered models with their configs."""
