"""Kubernetes jobs — one-shot batch workloads over kubectl."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kubernetes.kubernetes_client import (
    KubernetesClient,
    require_kubernetes_action,
)


class KubernetesJob:
    """Job lifecycle over kubectl."""

    def __init__(self, client: KubernetesClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def create(
        self, name: str, image: str, command: list[str] | None = None
    ) -> dict[str, Any]:
        require_kubernetes_action("job")
        args = ["create", "job", name, "--image=" + image]
        if command:
            args.append("--")
            args += command
        code, _, err = await self._client._run(args, timeout_s=60.0)
        self._metrics.increment("kubernetes.jobs.create")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def list(self) -> list[dict[str, Any]]:
        require_kubernetes_action("job")
        code, out, err = await self._client._run(
            ["get", "jobs", "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get jobs failed: {err.strip() or out.strip()}")
        self._metrics.increment("kubernetes.jobs.list")
        return self._client.first_json(out).get("items", [])

    async def delete(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("job")
        code, _, err = await self._client._run(["delete", "job", name], timeout_s=60.0)
        self._metrics.increment("kubernetes.jobs.delete")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def status(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("job")
        code, out, err = await self._client._run(
            ["get", "job", name, "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get job failed: {err.strip() or out.strip()}")
        obj = self._client.first_json(out)
        status = obj.get("status", {})
        return {
            "name": name,
            "succeeded": status.get("succeeded", 0),
            "failed": status.get("failed", 0),
            "active": status.get("active", 0),
        }


__all__ = ["KubernetesJob"]
