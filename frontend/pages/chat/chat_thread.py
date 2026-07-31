from __future__ import annotations

import logging
from typing import Any


class ChatThread:
    """In-memory conversation thread state."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.chat.thread")
        self._threads: dict[str, list[dict[str, Any]]] = {}

    def render(self, conversation_id: str) -> dict[str, Any]:
        return {
            "conversation_id": conversation_id,
            "messages": self.messages(conversation_id),
        }

    def messages(self, conversation_id: str) -> list[dict[str, Any]]:
        return list(self._threads.get(conversation_id, []))

    def append(self, conversation_id: str, message: dict[str, Any]) -> bool:
        self._threads.setdefault(conversation_id, []).append(message)
        return True
