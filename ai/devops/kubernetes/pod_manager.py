"""Pod manager."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class PodManager:
    def __init__(self) -> None:
        self._pods: Dict[str, Dict[str, Any]] = {}
    def create(self, name: str, namespace: str, image: str, replicas: int = 1) -> Dict[str, Any]:
        pod = {"name": name, "namespace": namespace, "image": image, "replicas": replicas, "status": "running", "created_at": time.time()}
        self._pods[name] = pod
        return pod
    def get(self, name: str) -> Dict[str, Any]:
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
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._pods.values())
    def list_by_namespace(self, namespace: str) -> List[Dict[str, Any]]:
        return [p for p in self._pods.values() if p.get("namespace") == namespace]
    def count(self) -> int:
        return len(self._pods)
