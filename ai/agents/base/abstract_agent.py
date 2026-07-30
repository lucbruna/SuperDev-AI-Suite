from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class AbstractAgent(ABC):
    """Abstract blueprint for all agents."""

    @abstractmethod
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_id(self) -> str:
        ...

    @abstractmethod
    def get_status(self) -> str:
        ...

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        ...
