from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseMemory(ABC):
    @abstractmethod
    async def store(self, key: str, value: Any) -> None: ...

    @abstractmethod
    async def retrieve(self, key: str) -> Any: ...

    @abstractmethod
    async def search(self, query: str) -> list[Any]: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def clear(self) -> None: ...
