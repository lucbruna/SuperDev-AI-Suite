from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .kubernetes_engine import KubernetesEngine


class PodManager:
    """Manages Kubernetes pods."""

    def __init__(self, engine: KubernetesEngine) -> None:
        self._log = logging.getLogger("superdev.devops.kubernetes.pods")
        self._engine = engine

    def create(self, name: str, image: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def delete(self, name: str, namespace: str = "default") -> bool:
        raise NotImplementedError

    def list(self, namespace: str = "default") -> list[dict[str, Any]]:
        raise NotImplementedError

    def logs(self, name: str, namespace: str = "default", tail: int = 100) -> list[str]:
        raise NotImplementedError

    def status(self, name: str, namespace: str = "default") -> dict[str, Any]:
        raise NotImplementedError
