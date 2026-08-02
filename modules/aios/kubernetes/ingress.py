"""Kubernetes ingresses — external HTTP routing over kubectl."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kubernetes.kubernetes_client import (
    KubernetesClient,
    require_kubernetes_action,
)


class KubernetesIngress:
    """Ingress lifecycle over kubectl."""

    def __init__(self, client: KubernetesClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def create(
        self,
        name: str,
        *,
        host: str,
        service: str,
        port: int,
    ) -> dict[str, Any]:
        require_kubernetes_action("ingress")
        rule = f"{host}/{service}:{port}"
        code, _, err = await self._client._run(
            ["create", "ingress", name, f"--rule={rule}"], timeout_s=60.0
        )
        self._metrics.increment("kubernetes.ingresses.create")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def list(self) -> list[dict[str, Any]]:
        require_kubernetes_action("ingress")
        code, out, err = await self._client._run(
            ["get", "ingresses", "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get ingresses failed: {err.strip() or out.strip()}")
        self._metrics.increment("kubernetes.ingresses.list")
        return self._client.first_json(out).get("items", [])

    async def delete(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("ingress")
        code, _, err = await self._client._run(["delete", "ingress", name], timeout_s=60.0)
        self._metrics.increment("kubernetes.ingresses.delete")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}


__all__ = ["KubernetesIngress"]
