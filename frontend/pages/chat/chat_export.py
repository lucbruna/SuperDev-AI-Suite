from __future__ import annotations

import json
import logging
from typing import Any


class ChatExport:
    """Exports conversation history."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.pages.chat.export")
        self._messages: dict[str, list[dict[str, Any]]] = {}

    def render(self) -> dict[str, Any]:
        return {"formats": ["json", "markdown"]}

    def to_json(self, conversation_id: str) -> str:
        messages = self._messages.get(conversation_id, [])
        return json.dumps(messages, indent=2, default=str)

    def to_markdown(self, conversation_id: str) -> str:
        lines = [f"# Conversation {conversation_id}", ""]
        for message in self._messages.get(conversation_id, []):
            role = message.get("role", "user")
            content = message.get("content", "")
            lines.append(f"**{role}:** {content}")
            lines.append("")
        return "\n".join(lines)
