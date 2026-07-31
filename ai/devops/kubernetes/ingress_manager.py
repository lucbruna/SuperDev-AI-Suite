"""Ingress manager."""
from __future__ import annotations
from typing import Any, Dict, List

class IngressManager:
    def __init__(self) -> None:
        self._ingresses: Dict[str, Dict[str, Any]] = {}
    def create(self, name: str, namespace: str, host: str, paths: List[Dict[str, str]] = None) -> Dict[str, Any]:
        ingress = {"name": name, "namespace": namespace, "host": host, "paths": paths or [], "status": "active"}
        self._ingresses[name] = ingress
        return ingress
    def add_path(self, name: str, path: str, service: str, port: int = 80) -> bool:
        if name not in self._ingresses:
            return False
        self._ingresses[name]["paths"].append({"path": path, "service": service, "port": port})
        return True
    def get(self, name: str) -> Dict[str, Any]:
        return self._ingresses.get(name, {"error": "not_found"})
    def delete(self, name: str) -> bool:
        if name in self._ingresses:
            del self._ingresses[name]
            return True
        return False
    def list_all(self) -> List[Dict[str, Any]]:
        return list(self._ingresses.values())
    def count(self) -> int:
        return len(self._ingresses)
