"""Conversation memory."""
from __future__ import annotations

import time
from typing import Any


class ConversationMemory:
    def __init__(self) -> None:
        self._conversations: dict[str, list[dict[str, Any]]] = {}
    def start(self, conversation_id: str) -> dict[str, Any]:
        self._conversations[conversation_id] = []
        return {"id": conversation_id, "started_at": time.time()}
    def add_message(self, conversation_id: str, role: str, content: str, metadata: dict[str, Any] = None) -> dict[str, Any]:
        if conversation_id not in self._conversations:
            self.start(conversation_id)
        msg = {"role": role, "content": content, "metadata": metadata or {}, "timestamp": time.time()}
        self._conversations[conversation_id].append(msg)
        return msg
    def get_messages(self, conversation_id: str, limit: int = 50) -> list[dict[str, Any]]:
        return self._conversations.get(conversation_id, [])[-limit:]
    def summarize(self, conversation_id: str) -> dict[str, Any]:
        msgs = self._conversations.get(conversation_id, [])
        user_msgs = [m for m in msgs if m["role"] == "user"]
        assistant_msgs = [m for m in msgs if m["role"] == "assistant"]
        return {"conversation_id": conversation_id, "total_messages": len(msgs), "user_messages": len(user_msgs), "assistant_messages": len(assistant_msgs)}
    def search(self, query: str) -> list[dict[str, Any]]:
        results = []
        for cid, msgs in self._conversations.items():
            for msg in msgs:
                if query.lower() in msg.get("content", "").lower():
                    results.append({"conversation_id": cid, "message": msg})
        return results
    def list_conversations(self) -> list[str]:
        return list(self._conversations.keys())
    def delete(self, conversation_id: str) -> bool:
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False
    def count(self) -> int:
        return sum(len(v) for v in self._conversations.values())
