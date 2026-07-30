from __future__ import annotations

import logging
from typing import Any


class SyntaxTree:
    """Represents and manipulates syntax trees."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.parsing.syntax")

    def build(self, tokens: list[dict[str, Any]]) -> dict[str, Any]:
        return {"type": "module", "children": []}
