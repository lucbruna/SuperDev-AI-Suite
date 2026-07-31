"""Digital Twin runtime."""
from __future__ import annotations

import time
from typing import Any


class TwinRuntime:
    def __init__(self) -> None:
        self._instances: dict[str, dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def create_instance(self, twin_id: str, config: dict[str, Any] = None) -> dict[str, Any]:
        instance = {"twin_id": twin_id, "config": config or {}, "status": "created", "created_at": time.time()}
        self._instances[twin_id] = instance
        return instance
    def start_instance(self, twin_id: str) -> dict[str, Any]:
        if twin_id not in self._instances:
            return {"error": "not_found"}
        self._instances[twin_id]["status"] = "running"
        self._instances[twin_id]["started_at"] = time.time()
        return self._instances[twin_id]
    def stop_instance(self, twin_id: str) -> dict[str, Any]:
        if twin_id not in self._instances:
            return {"error": "not_found"}
        self._instances[twin_id]["status"] = "stopped"
        return self._instances[twin_id]
    def get_instance(self, twin_id: str) -> dict[str, Any]:
        return self._instances.get(twin_id, {"error": "not_found"})
    def list_instances(self) -> list[dict[str, Any]]:
        return list(self._instances.values())
    def is_running(self) -> bool:
        return self._started
    def count(self) -> int:
        return len(self._instances)
