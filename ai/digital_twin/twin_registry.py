"""Digital Twin registry."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class TwinRegistry:
    def __init__(self) -> None:
        self._twins: Dict[str, Dict[str, Any]] = {}
    def register(self, twin_id: str, name: str, twin_type: str = "enterprise", **kwargs: Any) -> Dict[str, Any]:
        entry = {"twin_id": twin_id, "name": name, "type": twin_type, "status": "active", "registered_at": time.time(), **kwargs}
        self._twins[twin_id] = entry
        return entry
    def unregister(self, twin_id: str) -> bool:
        if twin_id in self._twins:
            self._twins[twin_id]["status"] = "inactive"
            return True
        return False
    def get(self, twin_id: str) -> Optional[Dict[str, Any]]:
        return self._twins.get(twin_id)
    def list_active(self) -> List[Dict[str, Any]]:
        return [t for t in self._twins.values() if t.get("status") == "active"]
    def list_by_type(self, twin_type: str) -> List[Dict[str, Any]]:
        return [t for t in self._twins.values() if t.get("type") == twin_type]
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._twins.values())
    def count(self) -> int:
        return len(self._twins)
    def update(self, twin_id: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        t = self._twins.get(twin_id)
        if t:
            t.update(kwargs)
            return t
        return None
