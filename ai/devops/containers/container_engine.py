"""Container engine."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class ContainerEngine:
    def __init__(self) -> None:
        self._containers: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def create(self, name: str, image: str, ports: List[int] = None, env: Dict[str, str] = None) -> Dict[str, Any]:
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
    def get(self, container_id: str) -> Dict[str, Any]:
        return self._containers.get(container_id, {"error": "not_found"})
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._containers.values())
    def list_running(self) -> List[Dict[str, Any]]:
        return [c for c in self._containers.values() if c["state"] == "running"]
    def count(self) -> int:
        return len(self._containers)
    def is_running(self) -> bool:
        return self._started
