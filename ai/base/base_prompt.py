from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BasePrompt(ABC):
    _template: str = ""

    @abstractmethod
    async def build(self, context: dict[str, Any]) -> str: ...

    @abstractmethod
    def get_template(self) -> str: ...
