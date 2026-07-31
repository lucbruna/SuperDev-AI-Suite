from __future__ import annotations

import logging
import time
from typing import Any

from ...frontend_context import FrontendContext


class ChatEngine:
    """Renders the AI chat page."""

    def __init__(self, context: FrontendContext | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.chat")
        self._context = context or FrontendContext()
        self._conversations: dict[str, list[dict[str, Any]]] = {}

    def render(self, **kwargs: Any) -> dict[str, Any]:
        return {
            "page": "chat",
            "conversations": len(self._conversations),
            "active": self.open(kwargs.get("conversation_id", "") if kwargs.get("conversation_id") else list(self._conversations)[0]) if self._conversations else {},
        }

    def conversations(self) -> list[dict[str, Any]]:
        return [
            {"conversation_id": cid, "messages": len(messages)}
            for cid, messages in self._conversations.items()
        ]

    def open(self, conversation_id: str) -> dict[str, Any]:
        if conversation_id not in self._conversations:
            raise KeyError(f"unknown conversation: {conversation_id}")
        return {
            "conversation_id": conversation_id,
            "messages": self._conversations[conversation_id],
        }

    def new(self) -> str:
        conversation_id = f"conv-{len(self._conversations) + 1}"
        self._conversations[conversation_id] = []
        return conversation_id

    def send(self, conversation_id: str, message: str) -> dict[str, Any]:
        if conversation_id not in self._conversations:
            raise KeyError(f"unknown conversation: {conversation_id}")
        entry = {"role": "user", "content": message, "ts": time.time()}
        self._conversations[conversation_id].append(entry)
        reply = {"role": "assistant", "content": f"Received: {message}", "ts": time.time()}
        self._conversations[conversation_id].append(reply)
        return reply
