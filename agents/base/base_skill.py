from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseSkill(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    async def execute(self, context: dict[str, Any], params: dict[str, Any]) -> dict[str, Any]:
        ...
