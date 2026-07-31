"""Context manager for conversations."""

from __future__ import annotations


class ContextManager:
    def __init__(self, max_context: int = 128000) -> None:
        self._max = max_context
        self._conversations: dict[str, list[dict[str, str]]] = {}

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        self._conversations.setdefault(conversation_id, []).append({"role": role, "content": content})

    def get_context(self, conversation_id: str, max_messages: int = 0) -> list[dict[str, str]]:
        messages = self._conversations.get(conversation_id, [])
        if max_messages:
            return messages[-max_messages:]
        return list(messages)

    def clear_context(self, conversation_id: str) -> int:
        n = len(self._conversations.get(conversation_id, []))
        self._conversations.pop(conversation_id, None)
        return n

    def context_length(self, conversation_id: str) -> int:
        messages = self._conversations.get(conversation_id, [])
        return sum(len(m.get("content", "").split()) for m in messages)

    def trim_context(self, conversation_id: str, keep_last: int = 10) -> int:
        messages = self._conversations.get(conversation_id, [])
        if len(messages) > keep_last:
            removed = len(messages) - keep_last
            self._conversations[conversation_id] = messages[-keep_last:]
            return removed
        return 0

    def list_conversations(self) -> list[str]:
        return list(self._conversations.keys())

    def message_count(self, conversation_id: str) -> int:
        return len(self._conversations.get(conversation_id, []))
