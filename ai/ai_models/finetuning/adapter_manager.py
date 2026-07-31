"""Adapter manager."""

from __future__ import annotations

import time
from typing import Any


class AdapterManager:
    def __init__(self) -> None:
        self._adapters: dict[str, dict[str, Any]] = {}

    def register(
        self, name: str, model_id: str, method: str, path: str, metadata: dict[str, Any] = None
    ) -> dict[str, Any]:
        adapter = {
            "name": name,
            "model_id": model_id,
            "method": method,
            "path": path,
            "metadata": metadata or {},
            "created_at": time.time(),
            "status": "active",
        }
        self._adapters[name] = adapter
        return adapter

    def get(self, name: str) -> dict[str, Any]:
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

    def list_active(self) -> list[dict[str, Any]]:
        return [a for a in self._adapters.values() if a["status"] == "active"]

    def list_all(self) -> list[str]:
        return list(self._adapters.keys())

    def count(self) -> int:
        return len(self._adapters)
