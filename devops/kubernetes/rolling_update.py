from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .kubernetes_engine import KubernetesEngine


class RollingUpdate:
    """Performs rolling updates for Kubernetes deployments."""

    def __init__(self, engine: KubernetesEngine) -> None:
        self._log = logging.getLogger("superdev.devops.kubernetes.rolling")
        self._engine = engine

    def update_image(self, deployment: str, image: str, namespace: str = "default", **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def pause(self, deployment: str, namespace: str = "default") -> bool:
        raise NotImplementedError

    def resume(self, deployment: str, namespace: str = "default") -> bool:
        raise NotImplementedError

    def status(self, deployment: str, namespace: str = "default") -> dict[str, Any]:
        raise NotImplementedError

    def rollout_undo(self, deployment: str, namespace: str = "default") -> dict[str, Any]:
        raise NotImplementedError
