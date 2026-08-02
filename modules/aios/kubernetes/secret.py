"""Kubernetes secrets — sensitive data as opaque literals over kubectl."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kubernetes.kubernetes_client import (
    KubernetesClient,
    require_kubernetes_action,
)


class KubernetesSecret:
    """Secret lifecycle over kubectl (generic/opaque)."""

    def __init__(self, client: KubernetesClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def create(self, name: str, data: dict[str, str]) -> dict[str, Any]:
        require_kubernetes_action("secret")
        args = ["create", "secret", "generic", name]
        for key, value in data.items():
            args.append(f"--from-literal={key}={value}")
        code, _, err = await self._client._run(args, timeout_s=60.0)
        self._metrics.increment("kubernetes.secrets.create")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def list(self) -> list[dict[str, Any]]:
        require_kubernetes_action("secret")
        code, out, err = await self._client._run(
            ["get", "secrets", "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get secrets failed: {err.strip() or out.strip()}")
        self._metrics.increment("kubernetes.secrets.list")
        return self._client.first_json(out).get("items", [])

    async def delete(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("secret")
        code, _, err = await self._client._run(["delete", "secret", name], timeout_s=60.0)
        self._metrics.increment("kubernetes.secrets.delete")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}


__all__ = ["KubernetesSecret"]
