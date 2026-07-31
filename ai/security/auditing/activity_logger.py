"""Activity logging."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid, json

class ActivityLogger:
    def __init__(self) -> None:
        self._logs: List[Dict[str, Any]] = []
        self._buffers: Dict[str, List[Dict[str, Any]]] = {}
    def log(self, category: str, action: str, user_id: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        entry = {"log_id": str(uuid.uuid4())[:8], "category": category, "action": action, "user_id": user_id, "details": details or {}, "timestamp": time.time()}
        self._logs.append(entry)
        self._buffers.setdefault(category, []).append(entry)
        return entry
    def get_by_category(self, category: str, limit: int = 100) -> List[Dict[str, Any]]:
        return self._buffers.get(category, [])[-limit:]
    def get_by_user(self, user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        return [e for e in self._logs if e["user_id"] == user_id][-limit:]
    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._logs[-limit:]
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        return [e for e in self._logs if keyword.lower() in json.dumps(e, default=str).lower()]
    def clear_category(self, category: str) -> int:
        n = len(self._buffers.get(category, []))
        self._buffers.pop(category, None)
        return n
    def count(self) -> int:
        return len(self._logs)
