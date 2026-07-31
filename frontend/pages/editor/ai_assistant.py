from __future__ import annotations

import logging
from typing import Any


class AIAssistant:
    """Inline AI completion and chat for the editor."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.editor.ai")

    def render(self) -> dict[str, Any]:
        return {"modes": ["complete", "chat"]}

    def complete(self, context: str, cursor: int) -> str:
        lines = context.splitlines()
        prefix = lines[-1] if lines else ""
        return f"# suggestion for: {prefix.strip()}"

    def chat(self, message: str) -> dict[str, Any]:
        return {"reply": f"AI: {message}", "actions": ["apply", "discard"]}

    def apply(self, patch: str) -> bool:
        return bool(patch)
