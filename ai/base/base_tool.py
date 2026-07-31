from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    _name: str = ""
    _description: str = ""
    _permissions: list[str] = []

    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def description(self) -> str: ...

    @abstractmethod
    def permissions(self) -> list[str]: ...

    @abstractmethod
    async def validate(self, params: dict[str, Any]) -> bool: ...

    @abstractmethod
    async def execute(self, params: dict[str, Any]) -> dict[str, Any]: ...

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
