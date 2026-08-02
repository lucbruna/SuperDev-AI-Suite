"""Kubernetes cluster — version, reachability and node inventory."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kubernetes.kubernetes_client import (
    KubernetesClient,
    require_kubernetes_action,
)


class KubernetesCluster:
    """Cluster-level operations over kubectl."""

    def __init__(self, client: KubernetesClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def version(self) -> dict[str, Any]:
        return await self._client.version()

    async def ping(self) -> bool:
        return await self._client.ping()

    async def nodes(self) -> list[dict[str, Any]]:
        require_kubernetes_action("cluster")
        code, out, err = await self._client._run(
            ["get", "nodes", "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get nodes failed: {err.strip() or out.strip()}")
        self._metrics.increment("kubernetes.cluster.nodes")
        return self._client.first_json(out).get("items", [])

    async def info(self) -> dict[str, Any]:
        require_kubernetes_action("cluster")
        code, out, err = await self._client._run(["cluster-info"], timeout_s=30.0)
        if code != 0:
            raise RuntimeError(f"kubectl cluster-info failed: {err.strip() or out.strip()}")
        return {"raw": out.strip()}


__all__ = ["KubernetesCluster"]
