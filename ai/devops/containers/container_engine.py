"""Container engine."""
from __future__ import annotations

import time
from typing import Any


class ContainerEngine:
    def __init__(self) -> None:
        self._containers: dict[str, dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def create(self, name: str, image: str, ports: list[int] = None, env: dict[str, str] = None) -> dict[str, Any]:
        import uuid
        cid = str(uuid.uuid4())[:8]
        container = {"container_id": cid, "name": name, "image": image, "state": "running", "ports": ports or [], "env": env or {}, "created_at": time.time()}
        self._containers[cid] = container
        return container
    def stop(self, container_id: str) -> bool:
        if container_id in self._containers:
            self._containers[container_id]["state"] = "stopped"
            return True
        return False
    def start_container(self, container_id: str) -> bool:
        if container_id in self._containers:
            self._containers[container_id]["state"] = "running"
            return True
        return False
    def remove(self, container_id: str) -> bool:
        if container_id in self._containers:
            del self._containers[container_id]
            return True
        return False
    def get(self, container_id: str) -> dict[str, Any]:
        return self._containers.get(container_id, {"error": "not_found"})
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._containers.values())
    def list_running(self) -> list[dict[str, Any]]:
        return [c for c in self._containers.values() if c["state"] == "running"]
    def count(self) -> int:
        return len(self._containers)
    def is_running(self) -> bool:
        return self._started
