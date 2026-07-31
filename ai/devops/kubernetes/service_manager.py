"""Service manager."""

from __future__ import annotations

from typing import Any


class ServiceManager:
    def __init__(self) -> None:
        self._services: dict[str, dict[str, Any]] = {}

    def create(
        self, name: str, namespace: str, service_type: str = "ClusterIP", ports: list[int] = None
    ) -> dict[str, Any]:
        service = {
            "name": name,
            "namespace": namespace,
            "type": service_type,
            "ports": ports or [80],
            "status": "active",
        }
        self._services[name] = service
        return service

    def get(self, name: str) -> dict[str, Any]:
        return self._services.get(name, {"error": "not_found"})

    def delete(self, name: str) -> bool:
        if name in self._services:
            del self._services[name]
            return True
        return False

    def list_all(self) -> list[dict[str, Any]]:
        return list(self._services.values())

    def list_by_namespace(self, namespace: str) -> list[dict[str, Any]]:
        return [s for s in self._services.values() if s.get("namespace") == namespace]

    def count(self) -> int:
        return len(self._services)
