from __future__ import annotations

import logging
import time
from typing import Any


class StatusBar:
    """Editor status bar state."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.editor.status")
        self._state: dict[str, Any] = {"mode": "normal"}
        self._messages: list[str] = []

    def render(self) -> dict[str, Any]:
        return {**self._state, "last_message": self._messages[-1] if self._messages else ""}

    def update(self, **kwargs: Any) -> None:
        self._state.update(kwargs)

    def message(self, text: str, timeout_ms: int = 3000) -> None:
        self._messages.append(f"{text} ({timeout_ms}ms)")
