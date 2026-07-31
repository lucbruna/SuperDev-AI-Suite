"""AI Model registry."""

from __future__ import annotations

import time
from typing import Any


class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[str, dict[str, Any]] = {}

    def register(
        self, model_id: str, name: str, provider: str, model_type: str = "llm", **kwargs: Any
    ) -> dict[str, Any]:
        entry = {
            "model_id": model_id,
            "name": name,
            "provider": provider,
            "type": model_type,
            "status": "active",
            "registered_at": time.time(),
            **kwargs,
        }
        self._models[model_id] = entry
        return entry

    def unregister(self, model_id: str) -> bool:
        if model_id in self._models:
            self._models[model_id]["status"] = "inactive"
            return True
        return False

    def get(self, model_id: str) -> dict[str, Any] | None:
        return self._models.get(model_id)

    def list_active(self) -> list[dict[str, Any]]:
        return [m for m in self._models.values() if m.get("status") == "active"]

    def list_by_provider(self, provider: str) -> list[dict[str, Any]]:
        return [m for m in self._models.values() if m.get("provider") == provider]

    def list_by_type(self, model_type: str) -> list[dict[str, Any]]:
        return [m for m in self._models.values() if m.get("type") == model_type]

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._models.values())

    def count(self) -> int:
        return len(self._models)

    def update(self, model_id: str, **kwargs: Any) -> dict[str, Any] | None:
        m = self._models.get(model_id)
        if m:
            m.update(kwargs)
            return m
        return None
