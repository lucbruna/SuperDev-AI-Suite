from __future__ import annotations

import logging
import time
from typing import Any


class ChatInput:
    """Composer for chat messages with attachments and suggestions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.chat.input")
        self._attachments: list[str] = []

    def render(self) -> dict[str, Any]:
        return {"attachments": list(self._attachments)}

    def send(self, text: str) -> dict[str, Any]:
        if not text.strip():
            raise ValueError("message cannot be empty")
        return {"role": "user", "content": text, "ts": time.time()}

    def attach(self, path: str) -> bool:
        self._attachments.append(path)
        return True

    def suggest(self, context: str) -> list[str]:
        return [
            "Explain the current file",
            "Find failing tests",
            "Suggest an improvement",
            "Generate documentation",
        ]
