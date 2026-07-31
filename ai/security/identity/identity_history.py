"""Identity history tracking."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, uuid

class IdentityHistory:
    def __init__(self) -> None:
        self._entries: List[Dict[str, Any]] = []
    def record(self, user_id: str, action: str, details: Dict[str, Any]) -> None:
        self._entries.append({"id": str(uuid.uuid4())[:8], "user_id": user_id, "action": action, "details": details, "timestamp": time.time()})
    def get(self, user_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        entries = [e for e in self._entries if user_id is None or e["user_id"] == user_id]
        return entries[-limit:]
    def count(self) -> int:
        return len(self._entries)
