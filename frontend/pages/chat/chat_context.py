from __future__ import annotations

import logging
from typing import Any


class ChatContext:
    """Conversation context references."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.chat.context")
        self._references: dict[str, list[dict[str, Any]]] = {}

    def render(self, conversation_id: str) -> dict[str, Any]:
        return {
            "conversation_id": conversation_id,
            "references": self.references(conversation_id),
        }

    def references(self, conversation_id: str) -> list[dict[str, Any]]:
        return list(self._references.get(conversation_id, []))

    def add_reference(self, conversation_id: str, ref: dict[str, Any]) -> bool:
        self._references.setdefault(conversation_id, []).append(ref)
        return True
