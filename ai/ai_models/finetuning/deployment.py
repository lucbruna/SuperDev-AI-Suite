"""Finetuning deployment."""
from __future__ import annotations

import time
from typing import Any


class DeploymentManager:
    def __init__(self) -> None:
        self._deployments: dict[str, dict[str, Any]] = {}
    def deploy(self, name: str, adapter_path: str, model_id: str, endpoint: str = "") -> dict[str, Any]:
        dep = {"name": name, "adapter_path": adapter_path, "model_id": model_id, "endpoint": endpoint, "status": "deployed", "deployed_at": time.time()}
        self._deployments[name] = dep
        return dep
    def undeploy(self, name: str) -> bool:
        if name in self._deployments:
            self._deployments[name]["status"] = "undeployed"
            return True
        return False
    def get(self, name: str) -> dict[str, Any]:
        return self._deployments.get(name, {"error": "not_found"})
    def list_active(self) -> list[dict[str, Any]]:
        return [d for d in self._deployments.values() if d["status"] == "deployed"]
    def list_all(self) -> list[str]:
        return list(self._deployments.keys())
    def delete(self, name: str) -> bool:
        if name in self._deployments:
            del self._deployments[name]
            return True
        return False
    def rollback(self, name: str) -> dict[str, Any]:
        if name not in self._deployments:
            return {"error": "not_found"}
        self._deployments[name]["status"] = "deployed"
        self._deployments[name]["rolled_back_at"] = time.time()
        return self._deployments[name]
    def count(self) -> int:
        return len(self._deployments)
