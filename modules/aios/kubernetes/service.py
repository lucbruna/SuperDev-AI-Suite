"""Kubernetes services — stable network endpoints over kubectl."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kubernetes.kubernetes_client import (
    KubernetesClient,
    require_kubernetes_action,
)


class KubernetesService:
    """Service lifecycle over kubectl."""

    def __init__(self, client: KubernetesClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def create(
        self,
        name: str,
        *,
        port: int,
        target_port: int | None = None,
        service_type: str = "ClusterIP",
    ) -> dict[str, Any]:
        require_kubernetes_action("service")
        tcp = str(port) if target_port is None else f"{port}:{target_port}"
        code, _, err = await self._client._run(
            [
                "create",
                "service",
                service_type,
                name,
                f"--tcp={tcp}",
            ],
            timeout_s=60.0,
        )
        self._metrics.increment("kubernetes.services.create")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def list(self) -> list[dict[str, Any]]:
        require_kubernetes_action("service")
        code, out, err = await self._client._run(
            ["get", "services", "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get services failed: {err.strip() or out.strip()}")
        self._metrics.increment("kubernetes.services.list")
        return self._client.first_json(out).get("items", [])

    async def get(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("service")
        code, out, err = await self._client._run(
            ["get", "service", name, "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get service failed: {err.strip() or out.strip()}")
        obj = self._client.first_json(out)
        return {
            "name": name,
            "type": obj.get("spec", {}).get("type"),
            "cluster_ip": obj.get("spec", {}).get("clusterIP"),
            "ports": obj.get("spec", {}).get("ports", []),
        }

    async def delete(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("service")
        code, _, err = await self._client._run(["delete", "service", name], timeout_s=60.0)
        self._metrics.increment("kubernetes.services.delete")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}


__all__ = ["KubernetesService"]
