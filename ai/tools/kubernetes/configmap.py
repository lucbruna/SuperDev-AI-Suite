from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class KubernetesConfigMap(BaseTool):
    """Manage Kubernetes ConfigMaps."""

    _name = "kubernetes_configmap"
    _description = "Manage Kubernetes ConfigMaps: list, get, create, update, delete"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._configmaps: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "")
        namespace = params.get("namespace", "default")
        try:
            if action == "list":
                return {
                    "success": True,
                    "configmaps": self._configmaps,
                    "namespace": namespace,
                    "count": len(self._configmaps),
                }
            elif action == "get":
                name = params.get("name", "")
                cm = next((c for c in self._configmaps if c.get("name") == name), None)
                if not cm:
                    return {"success": False, "error": f"ConfigMap not found: {name}"}
                return {"success": True, "configmap": cm}
            elif action == "create":
                cm = {
                    "name": params.get("name", f"cm-{len(self._configmaps) + 1}"),
                    "data": params.get("data", {}),
                    "namespace": namespace,
                }
                self._configmaps.append(cm)
                return {"success": True, "configmap": cm}
            elif action == "update":
                name = params.get("name", "")
                for cm in self._configmaps:
                    if cm.get("name") == name:
                        if "data" in params:
                            cm["data"] = params["data"]
                        return {"success": True, "configmap": cm}
                return {"success": False, "error": f"ConfigMap not found: {name}"}
            elif action == "delete":
                name = params.get("name", "")
                self._configmaps = [c for c in self._configmaps if c.get("name") != name]
                return {"success": True, "message": f"Deleted ConfigMap {name}"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        self._configmaps.clear()
