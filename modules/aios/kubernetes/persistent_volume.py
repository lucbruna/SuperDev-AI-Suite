"""Kubernetes persistent volumes — PVC lifecycle over kubectl."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kubernetes.kubernetes_client import (
    KubernetesClient,
    require_kubernetes_action,
)


class KubernetesPersistentVolume:
    """PersistentVolumeClaim lifecycle over kubectl."""

    def __init__(self, client: KubernetesClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def create(
        self,
        name: str,
        *,
        size: str = "1Gi",
        storage_class: str | None = None,
    ) -> dict[str, Any]:
        require_kubernetes_action("volume")
        args = ["create", "pvc", name, f"--size={size}"]
        if storage_class is not None:
            args.append(f"--storage-class={storage_class}")
        code, _, err = await self._client._run(args, timeout_s=60.0)
        self._metrics.increment("kubernetes.pvc.create")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def list(self) -> list[dict[str, Any]]:
        require_kubernetes_action("volume")
        code, out, err = await self._client._run(
            ["get", "pvc", "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get pvc failed: {err.strip() or out.strip()}")
        self._metrics.increment("kubernetes.pvc.list")
        return self._client.first_json(out).get("items", [])

    async def delete(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("volume")
        code, _, err = await self._client._run(["delete", "pvc", name], timeout_s=60.0)
        self._metrics.increment("kubernetes.pvc.delete")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}


__all__ = ["KubernetesPersistentVolume"]
