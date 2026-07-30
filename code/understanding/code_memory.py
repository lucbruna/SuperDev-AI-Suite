from __future__ import annotations

import logging
from typing import Any


class CodeMemory:
    """Maintains memory of code structures across sessions."""

    def __init__(self) -> None:
        self._memory: dict[str, Any] = {}
        self._log = logging.getLogger("superdev.code.understanding.memory")

    def remember(self, key: str, value: Any) -> None:
        self._memory[key] = value

    def recall(self, key: str) -> Any | None:
        return self._memory.get(key)
