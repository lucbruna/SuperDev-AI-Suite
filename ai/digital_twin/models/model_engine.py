"""Model engine for digital twin modeling."""

from __future__ import annotations

import time
from typing import Any


class ModelEngine:
    def __init__(self) -> None:
        self._models: dict[str, dict[str, Any]] = {}
        self._started = False

    def start(self) -> None:
        self._started = True

    def create(
        self, model_id: str, name: str, model_type: str = "entity", schema: dict[str, Any] = None
    ) -> dict[str, Any]:
        model = {
            "model_id": model_id,
            "name": name,
            "type": model_type,
            "schema": schema or {},
            "instances": [],
            "created_at": time.time(),
        }
        self._models[model_id] = model
        return model

    def get(self, model_id: str) -> dict[str, Any]:
        return self._models.get(model_id, {"error": "not_found"})

    def update(self, model_id: str, **kwargs: Any) -> bool:
        if model_id not in self._models:
            return False
        self._models[model_id].update(kwargs)
        return True

    def delete(self, model_id: str) -> bool:
        if model_id in self._models:
            del self._models[model_id]
            return True
        return False

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._models.values())

    def list_by_type(self, model_type: str) -> list[dict[str, Any]]:
        return [m for m in self._models.values() if m.get("type") == model_type]

    def add_instance(self, model_id: str, instance: dict[str, Any]) -> bool:
        if model_id not in self._models:
            return False
        self._models[model_id]["instances"].append(instance)
        return True

    def count(self) -> int:
        return len(self._models)

    def is_running(self) -> bool:
        return self._started
