from __future__ import annotations

import difflib
import logging
from typing import Any


class DiffView:
    """Side-by-side diff visualization."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.editor.diff")
        self._last: dict[str, Any] = {}

    def render(self) -> dict[str, Any]:
        return {"has_diff": bool(self._last)}

    def compare(self, original: str, modified: str) -> dict[str, Any]:
        diff = list(difflib.unified_diff(original.splitlines(), modified.splitlines(), lineterm=""))
        self._last = {
            "original_lines": len(original.splitlines()),
            "modified_lines": len(modified.splitlines()),
            "hunks": diff,
        }
        return self._last

    def accept(self, side: str) -> str:
        if side not in ("original", "modified"):
            raise ValueError(f"unknown side: {side}")
        return "accepted"
