from __future__ import annotations

import logging
from typing import Any


class ASTManager:
    """Manages Abstract Syntax Tree operations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.parsing.ast")

    def parse(self, code: str) -> dict[str, Any] | None:
        return None

    def to_dict(self, node: Any) -> dict[str, Any]:
        return {}
