from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Abstract adapter for provider-specific format conversion."""

    @abstractmethod
    async def adapt_request(self, request: Any) -> Any:
        ...

    @abstractmethod
    async def adapt_response(self, response: Any) -> Any:
        ...

    def to_dict(self) -> dict[str, Any]:
        return {"type": self.__class__.__name__}
