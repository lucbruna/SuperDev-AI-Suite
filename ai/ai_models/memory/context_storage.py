"""Context storage."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class ContextStorage:
    def __init__(self, max_tokens: int = 4000) -> None:
        self._contexts: Dict[str, List[Dict[str, Any]]] = {}
        self._max_tokens = max_tokens
    def add(self, session_id: str, content: str, role: str = "user", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        entry = {"content": content, "role": role, "metadata": metadata or {}, "timestamp": time.time()}
        self._contexts.setdefault(session_id, []).append(entry)
        return entry
    def get_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        return self._contexts.get(session_id, [])[-limit:]
    def get_context_window(self, session_id: str, max_messages: int = 10) -> List[Dict[str, Any]]:
        history = self._contexts.get(session_id, [])
        return history[-max_messages:]
    def truncate(self, session_id: str, keep_last: int = 10) -> int:
        if session_id not in self._contexts:
            return 0
        history = self._contexts[session_id]
        removed = max(0, len(history) - keep_last)
        self._contexts[session_id] = history[-keep_last:]
        return removed
    def delete_session(self, session_id: str) -> bool:
        if session_id in self._contexts:
            del self._contexts[session_id]
            return True
        return False
    def list_sessions(self) -> List[str]:
        return list(self._contexts.keys())
    def token_estimate(self, session_id: str) -> int:
        return sum(len(str(m.get("content", ""))) // 4 for m in self._contexts.get(session_id, []))
    def clear(self, session_id: str = "") -> int:
        if session_id:
            n = len(self._contexts.get(session_id, []))
            self._contexts.pop(session_id, None)
            return n
        total = sum(len(v) for v in self._contexts.values())
        self._contexts.clear()
        return total
