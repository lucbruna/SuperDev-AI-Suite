"""Kubernetes deployments — long-running workloads with replica scaling."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_metrics import get_kernel_metrics
from modules.aios.kubernetes.kubernetes_client import (
    KubernetesClient,
    require_kubernetes_action,
)


class KubernetesDeployment:
    """Deployment lifecycle over kubectl."""

    def __init__(self, client: KubernetesClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def create(
        self,
        name: str,
        image: str,
        *,
        replicas: int = 1,
        port: int | None = None,
    ) -> dict[str, Any]:
        require_kubernetes_action("deployment")
        args = [
            "create",
            "deployment",
            name,
            "--image=" + image,
            f"--replicas={replicas}",
        ]
        if port is not None:
            args.append(f"--port={port}")
        code, _, err = await self._client._run(args, timeout_s=60.0)
        self._metrics.increment("kubernetes.deployments.create")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def scale(self, name: str, replicas: int) -> dict[str, Any]:
        require_kubernetes_action("deployment")
        code, _, err = await self._client._run(
            ["scale", "deployment", name, f"--replicas={replicas}"], timeout_s=60.0
        )
        self._metrics.increment("kubernetes.deployments.scale")
        return {"name": name, "replicas": replicas, "ok": code == 0, "error": err.strip() if code else ""}

    async def list(self) -> list[dict[str, Any]]:
        require_kubernetes_action("deployment")
        code, out, err = await self._client._run(
            ["get", "deployments", "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get deployments failed: {err.strip() or out.strip()}")
        self._metrics.increment("kubernetes.deployments.list")
        return self._client.first_json(out).get("items", [])

    async def delete(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("deployment")
        code, _, err = await self._client._run(["delete", "deployment", name], timeout_s=60.0)
        self._metrics.increment("kubernetes.deployments.delete")
        return {"name": name, "ok": code == 0, "error": err.strip() if code else ""}

    async def status(self, name: str) -> dict[str, Any]:
        require_kubernetes_action("deployment")
        code, out, err = await self._client._run(
            ["get", "deployment", name, "-o", "json"], timeout_s=60.0
        )
        if code != 0:
            raise RuntimeError(f"kubectl get deployment failed: {err.strip() or out.strip()}")
        obj = self._client.first_json(out)
        status = obj.get("status", {})
        return {
            "name": name,
            "replicas": status.get("replicas", 0),
            "ready": status.get("readyReplicas", 0),
            "available": status.get("availableReplicas", 0),
        }


__all__ = ["KubernetesDeployment"]
