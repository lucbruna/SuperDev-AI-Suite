from __future__ import annotations

import logging
from typing import Any


class ChatTools:
    """Renders tool call results and approval flows."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.chat.tools")
        self._pending: dict[str, dict[str, Any]] = {}

    def render(self, result: dict[str, Any]) -> dict[str, Any]:
        return {"result": result, "pending": len(self._pending)}

    def render_diff(self, patch: str) -> dict[str, Any]:
        lines = patch.splitlines()
        return {"type": "diff", "lines": len(lines), "added": sum(1 for l in lines if l.startswith("+") and not l.startswith("+++"))}

    def approve(self, tool_call_id: str) -> bool:
        call = self._pending.pop(tool_call_id, None)
        return call is not None
