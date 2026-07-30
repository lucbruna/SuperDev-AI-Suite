from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator


class AIProvider(ABC):
    """Protocol for AI model providers."""

    @abstractmethod
    async def chat(self, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        """Send a chat completion request."""

    @abstractmethod
    async def stream(self, messages: list[dict[str, Any]], **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        """Stream a chat completion response."""

    @abstractmethod
    async def embeddings(self, texts: list[str], **kwargs: Any) -> list[list[float]]:
        """Generate embeddings for texts."""


class AIAgent(ABC):
    """Protocol for AI agents."""

    @abstractmethod
    async def execute(self, task: str, **kwargs: Any) -> dict[str, Any]:
        """Execute a task."""

    @abstractmethod
    async def cancel(self) -> None:
        """Cancel the current execution."""

    @abstractmethod
    def status(self) -> str:
        """Get current agent status."""


class AITool(ABC):
    """Protocol for AI tools."""

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with given arguments."""

    @abstractmethod
    def validate(self, **kwargs: Any) -> bool:
        """Validate tool arguments."""


class AIMemory(ABC):
    """Protocol for AI memory backends."""

    @abstractmethod
    async def store(self, key: str, value: Any, **kwargs: Any) -> None:
        """Store a value in memory."""

    @abstractmethod
    async def retrieve(self, key: str) -> Any:
        """Retrieve a value from memory."""

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search memory by semantic similarity."""

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a value from memory."""


class AIRouter(ABC):
    """Protocol for AI request routing."""

    @abstractmethod
    def route(self, request: dict[str, Any], context: dict[str, Any] | None = None) -> tuple[str, str]:
        """Route a request to the appropriate provider and model."""


class AIEventHandler(ABC):
    """Protocol for AI event handlers."""

    @abstractmethod
    async def handle_event(self, event_type: str, data: dict[str, Any]) -> None:
        """Handle an AI event."""
