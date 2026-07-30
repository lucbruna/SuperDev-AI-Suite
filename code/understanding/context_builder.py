from __future__ import annotations

import logging
from typing import Any


class ContextBuilder:
    """Builds execution context for code understanding."""

    def __init__(self) -> None:
        self._context: dict[str, Any] = {}
        self._log = logging.getLogger("superdev.code.understanding.context")

    def add(self, key: str, value: Any) -> None:
        self._context[key] = value

    def build(self) -> dict[str, Any]:
        return dict(self._context)
