from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AbstractAgent(ABC):
    """Abstract blueprint for all agents."""

    @abstractmethod
    def execute(self, task: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_id(self) -> str:
        ...

    @abstractmethod
    def get_status(self) -> str:
        ...

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        ...
