from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PlannerTool(ABC):
    """Protocol for planner tools."""

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Execute the tool."""

    @abstractmethod
    def validate(self, **kwargs: Any) -> bool:
        """Validate tool arguments."""


class PlannerStorage(ABC):
    """Protocol for planner storage backends."""

    @abstractmethod
    def save(self, key: str, value: Any) -> None: ...

    @abstractmethod
    def load(self, key: str) -> Any | None: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...

    @abstractmethod
    def list_keys(self) -> list[str]: ...
