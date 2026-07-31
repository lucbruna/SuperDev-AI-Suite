"""Adapter manager."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class AdapterManager:
    def __init__(self) -> None:
        self._adapters: Dict[str, Dict[str, Any]] = {}
    def register(self, name: str, model_id: str, method: str, path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        adapter = {"name": name, "model_id": model_id, "method": method, "path": path, "metadata": metadata or {}, "created_at": time.time(), "status": "active"}
        self._adapters[name] = adapter
        return adapter
    def get(self, name: str) -> Dict[str, Any]:
        return self._adapters.get(name, {"error": "not_found"})
    def deactivate(self, name: str) -> bool:
        if name in self._adapters:
            self._adapters[name]["status"] = "inactive"
            return True
        return False
    def activate(self, name: str) -> bool:
        if name in self._adapters:
            self._adapters[name]["status"] = "active"
            return True
        return False
    def delete(self, name: str) -> bool:
        if name in self._adapters:
            del self._adapters[name]
            return True
        return False
    def list_active(self) -> List[Dict[str, Any]]:
        return [a for a in self._adapters.values() if a["status"] == "active"]
    def list_all(self) -> List[str]:
        return list(self._adapters.keys())
    def count(self) -> int:
        return len(self._adapters)
