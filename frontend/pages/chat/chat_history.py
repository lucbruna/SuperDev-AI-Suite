from __future__ import annotations

import logging
from typing import Any


class ChatHistory:
    """Conversation history list, search and delete."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.chat.history")
        self._conversations: dict[str, dict[str, Any]] = {}

    def render(self) -> dict[str, Any]:
        return {"conversations": self.list(), "count": len(self._conversations)}

    def list(self) -> list[dict[str, Any]]:
        return [
            {"conversation_id": cid, **meta}
            for cid, meta in self._conversations.items()
        ]

    def search(self, query: str) -> list[dict[str, Any]]:
        return [
            {"conversation_id": cid, **meta}
            for cid, meta in self._conversations.items()
            if query.lower() in str(meta).lower()
        ]

    def delete(self, conversation_id: str) -> bool:
        return self._conversations.pop(conversation_id, None) is not None
