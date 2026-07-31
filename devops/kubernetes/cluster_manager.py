from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .kubernetes_engine import KubernetesEngine


class ClusterManager:
    """Manages Kubernetes clusters — create, connect, scale, delete."""

    def __init__(self, engine: KubernetesEngine) -> None:
        self._log = logging.getLogger("superdev.devops.kubernetes.clusters")
        self._engine = engine

    def create(self, name: str, provider: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def connect(self, name: str, kubeconfig: str | None = None) -> bool:
        raise NotImplementedError

    def delete(self, name: str) -> bool:
        raise NotImplementedError

    def list(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def status(self, name: str) -> dict[str, Any]:
        raise NotImplementedError
