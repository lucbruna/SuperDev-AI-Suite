"""Kubernetes configmaps — non-secret configuration data over kubectl."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kubernetes.kubernetes_client import (
    KubernetesClient,
    require_kubernetes_action,
)


class KubernetesConfigMap:
    """ConfigMap lifecycle over kubectl."""

    def __init__(self, client: KubernetesClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def create(self, name: str, data: dict[str, str]) -> dict[str, Any]:
        require_kubernetes_action("configmap")
        args = ["create", "configmap", name]
        for key, value in data.items():
            args.append(f"--from-literal={key}={value}")
        code, _, err = await self._client._run(args, timeout_s=60.0)
        self._metrics.increment("kubernetes.configmaps.create")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def list(self) -> list[dict[str, Any]]:
        require_kubernetes_action("configmap")
        code, out, err = await self._client._run(
            ["get", "configmaps", "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get configmaps failed: {err.strip() or out.strip()}")
        self._metrics.increment("kubernetes.configmaps.list")
        return self._client.first_json(out).get("items", [])

    async def get(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("configmap")
        code, out, err = await self._client._run(
            ["get", "configmap", name, "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get configmap failed: {err.strip() or out.strip()}")
        obj = self._client.first_json(out)
        return {
            "name": name,
            "data": obj.get("data", {}),
        }

    async def delete(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("configmap")
        code, _, err = await self._client._run(["delete", "configmap", name], timeout_s=60.0)
        self._metrics.increment("kubernetes.configmaps.delete")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}


__all__ = ["KubernetesConfigMap"]
