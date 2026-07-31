"""AI Model registry."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class ModelRegistry:
    def __init__(self) -> None:
        self._models: Dict[str, Dict[str, Any]] = {}
    def register(self, model_id: str, name: str, provider: str, model_type: str = "llm", **kwargs: Any) -> Dict[str, Any]:
        entry = {"model_id": model_id, "name": name, "provider": provider, "type": model_type, "status": "active", "registered_at": time.time(), **kwargs}
        self._models[model_id] = entry
        return entry
    def unregister(self, model_id: str) -> bool:
        if model_id in self._models:
            self._models[model_id]["status"] = "inactive"
            return True
        return False
    def get(self, model_id: str) -> Optional[Dict[str, Any]]:
        return self._models.get(model_id)
    def list_active(self) -> List[Dict[str, Any]]:
        return [m for m in self._models.values() if m.get("status") == "active"]
    def list_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        return [m for m in self._models.values() if m.get("provider") == provider]
    def list_by_type(self, model_type: str) -> List[Dict[str, Any]]:
        return [m for m in self._models.values() if m.get("type") == model_type]
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._models.values())
    def count(self) -> int:
        return len(self._models)
    def update(self, model_id: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        m = self._models.get(model_id)
        if m:
            m.update(kwargs)
            return m
        return None
