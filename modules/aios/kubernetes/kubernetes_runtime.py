"""Kubernetes runtime — facade over cluster resources (Volume 12, Fase 16)."""
from __future__ import annotations

from typing import Any

from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kubernetes.cluster import KubernetesCluster
from modules.aios.kubernetes.configmap import KubernetesConfigMap
from modules.aios.kubernetes.deployment import KubernetesDeployment
from modules.aios.kubernetes.ingress import KubernetesIngress
from modules.aios.kubernetes.job import KubernetesJob
from modules.aios.kubernetes.kubernetes_client import (
    KubernetesClient,
    KubernetesUnavailableError,
)
from modules.aios.kubernetes.namespace import KubernetesNamespace
from modules.aios.kubernetes.persistent_volume import KubernetesPersistentVolume
from modules.aios.kubernetes.secret import KubernetesSecret
from modules.aios.kubernetes.service import KubernetesService


class KubernetesRuntime:
    """Facade over the kubernetes integration.

    Stateless: sub-managers are kubectl CLI wrappers. ``close`` is a no-op.
    Degrades gracefully when no cluster context is configured
    (:meth:`available` returns False).
    """

    def __init__(self) -> None:
        self.client = KubernetesClient()
        self.cluster = KubernetesCluster(self.client)
        self.namespaces = KubernetesNamespace(self.client)
        self.jobs = KubernetesJob(self.client)
        self.deployments = KubernetesDeployment(self.client)
        self.services = KubernetesService(self.client)
        self.ingresses = KubernetesIngress(self.client)
        self.configmaps = KubernetesConfigMap(self.client)
        self.secrets = KubernetesSecret(self.client)
        self.volumes = KubernetesPersistentVolume(self.client)
        self._logger = get_kernel_logger()

    async def available(self) -> bool:
        return await self.client.ping()

    async def version(self) -> dict[str, Any]:
        return await self.client.version()

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort aggregate state; degrades cleanly without a cluster."""
        state: dict[str, Any] = {
            "available": False,
            "version": {},
            "namespaces": [],
            "jobs": [],
            "deployments": [],
            "services": [],
            "ingresses": [],
            "configmaps": [],
            "secrets": [],
            "pvc": [],
        }
        try:
            state["available"] = await self.client.ping()
        except KubernetesUnavailableError:
            return state
        if not state["available"]:
            return state

        async def _safe(coro: Any) -> list[dict[str, Any]]:
            try:
                return await coro
            except Exception:  # noqa: BLE001
                return []

        try:
            state["version"] = await self.client.version()
        except (KubernetesUnavailableError, RuntimeError):
            state["version"] = {}
        state["namespaces"] = await _safe(self.namespaces.list())
        state["jobs"] = await _safe(self.jobs.list())
        state["deployments"] = await _safe(self.deployments.list())
        state["services"] = await _safe(self.services.list())
        state["ingresses"] = await _safe(self.ingresses.list())
        state["configmaps"] = await _safe(self.configmaps.list())
        state["secrets"] = await _safe(self.secrets.list())
        state["pvc"] = await _safe(self.volumes.list())
        return state

    async def close(self) -> None:
        """No-op — the kubernetes runtime is stateless. Resources are not deleted."""


_kubernetes_runtime: KubernetesRuntime | None = None


def get_kubernetes_runtime() -> KubernetesRuntime:
    global _kubernetes_runtime
    if _kubernetes_runtime is None:
        _kubernetes_runtime = KubernetesRuntime()
    return _kubernetes_runtime


__all__ = ["KubernetesRuntime", "get_kubernetes_runtime"]
