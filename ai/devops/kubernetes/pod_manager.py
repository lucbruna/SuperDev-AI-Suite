"""Pod manager."""
from __future__ import annotations

import time
from typing import Any


class PodManager:
    def __init__(self) -> None:
        self._pods: dict[str, dict[str, Any]] = {}
    def create(self, name: str, namespace: str, image: str, replicas: int = 1) -> dict[str, Any]:
        pod = {"name": name, "namespace": namespace, "image": image, "replicas": replicas, "status": "running", "created_at": time.time()}
        self._pods[name] = pod
        return pod
    def get(self, name: str) -> dict[str, Any]:
        return self._pods.get(name, {"error": "not_found"})
    def delete(self, name: str) -> bool:
        if name in self._pods:
            del self._pods[name]
            return True
        return False
    def scale(self, name: str, replicas: int) -> bool:
        if name in self._pods:
            self._pods[name]["replicas"] = replicas
            return True
        return False
    def list_all(self) -> list[dict[str, Any]]:
        return list(self._pods.values())
    def list_by_namespace(self, namespace: str) -> list[dict[str, Any]]:
        return [p for p in self._pods.values() if p.get("namespace") == namespace]
    def count(self) -> int:
        return len(self._pods)
