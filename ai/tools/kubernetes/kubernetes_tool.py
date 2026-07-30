from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .pod import KubernetesPod
from .service import KubernetesService
from .deployment import KubernetesDeployment
from .namespace import KubernetesNamespace
from .configmap import KubernetesConfigMap


class KubernetesTool(BaseTool):
    """Composite Kubernetes tool for cluster operations."""

    _name = "kubernetes"
    _description = "Kubernetes operations: pods, services, deployments, namespaces, configmaps"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._pod = KubernetesPod()
        self._service = KubernetesService()
        self._deployment = KubernetesDeployment()
        self._namespace = KubernetesNamespace()
        self._configmap = KubernetesConfigMap()

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        sub_tool = params.get("sub_tool", "")
        action = params.get("action", "")

        if sub_tool == "pod" or action in ("list_pods", "get_pod", "pod_logs"):
            return await self._pod.execute(params)
        elif sub_tool == "service":
            return await self._service.execute(params)
        elif sub_tool == "deployment":
            return await self._deployment.execute(params)
        elif sub_tool == "namespace":
            return await self._namespace.execute(params)
        elif sub_tool == "configmap":
            return await self._configmap.execute(params)
        return {"success": False, "error": f"Unknown Kubernetes action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        for tool in (self._pod, self._service, self._deployment, self._namespace, self._configmap):
            await tool.cleanup()
