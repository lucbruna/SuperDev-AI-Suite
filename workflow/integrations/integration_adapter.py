from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IntegrationAdapter(ABC):
    """Abstract base for integration adapters."""

    @abstractmethod
    def execute(self, action: str, data: dict[str, Any]) -> Any:
        ...
