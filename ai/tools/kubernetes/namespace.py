from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class KubernetesNamespace(BaseTool):
    """Manage Kubernetes namespaces."""

    _name = "kubernetes_namespace"
    _description = "Manage Kubernetes namespaces: list, get, create, delete"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._namespaces: list[dict[str, Any]] = [{"name": "default", "status": "Active"}]

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
        try:
            if action == "list":
                return {"success": True, "namespaces": self._namespaces, "count": len(self._namespaces)}
            elif action == "get":
                name = params.get("name", "")
                ns = next((n for n in self._namespaces if n.get("name") == name), None)
                if not ns:
                    return {"success": False, "error": f"Namespace not found: {name}"}
                return {"success": True, "namespace": ns}
            elif action == "create":
                name = params.get("name", f"ns-{len(self._namespaces)}")
                ns = {"name": name, "status": "Active"}
                self._namespaces.append(ns)
                return {"success": True, "namespace": ns}
            elif action == "delete":
                name = params.get("name", "")
                if name == "default":
                    return {"success": False, "error": "Cannot delete default namespace"}
                self._namespaces = [n for n in self._namespaces if n.get("name") != name]
                return {"success": True, "message": f"Deleted namespace {name}"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        self._namespaces = [{"name": "default", "status": "Active"}]
