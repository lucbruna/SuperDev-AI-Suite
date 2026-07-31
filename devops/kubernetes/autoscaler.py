from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .kubernetes_engine import KubernetesEngine


class Autoscaler:
    """Manages Kubernetes Horizontal Pod Autoscalers."""

    def __init__(self, engine: KubernetesEngine) -> None:
        self._log = logging.getLogger("superdev.devops.kubernetes.autoscaler")
        self._engine = engine

    def create(self, name: str, deployment: str, min_replicas: int, max_replicas: int, cpu_target: int = 80, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def update(self, name: str, min_replicas: int, max_replicas: int, namespace: str = "default") -> dict[str, Any]:
        raise NotImplementedError

    def delete(self, name: str, namespace: str = "default") -> bool:
        raise NotImplementedError

    def list(self, namespace: str = "default") -> list[dict[str, Any]]:
        raise NotImplementedError
