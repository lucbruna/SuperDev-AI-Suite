"""Kubernetes namespaces — list, create, delete and probe namespaces."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kubernetes.kubernetes_client import (
    KubernetesClient,
    require_kubernetes_action,
)


class KubernetesNamespace:
    """Namespace lifecycle over kubectl."""

    def __init__(self, client: KubernetesClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def list(self) -> list[dict[str, Any]]:
        require_kubernetes_action("namespace")
        code, out, err = await self._client._run(
            ["get", "namespaces", "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get namespaces failed: {err.strip() or out.strip()}")
        self._metrics.increment("kubernetes.namespaces.list")
        return self._client.first_json(out).get("items", [])

    async def create(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("namespace")
        code, _, err = await self._client._run(
            ["create", "namespace", name], timeout_s=60.0
        )
        self._metrics.increment("kubernetes.namespaces.create")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def delete(self, name: str, *, force: bool = False) -> dict[str, Any]:
        require_kubernetes_action("namespace")
        args = ["delete", "namespace", name]
        if force:
            args += ["--grace-period=0", "--force"]
        code, _, err = await self._client._run(args, timeout_s=60.0)
        self._metrics.increment("kubernetes.namespaces.delete")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def exists(self, name: str) -> bool:
        require_kubernetes_action("namespace")
        items = await self.list()
        return any(i.get("metadata", {}).get("name") == name for i in items)


__all__ = ["KubernetesNamespace"]
