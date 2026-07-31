from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .kubernetes_engine import KubernetesEngine


class KubernetesService:
    """Manages Kubernetes Services."""

    def __init__(self, engine: KubernetesEngine) -> None:
        self._log = logging.getLogger("superdev.devops.kubernetes.services")
        self._engine = engine

    def create(self, name: str, selector: dict[str, str], ports: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def delete(self, name: str, namespace: str = "default") -> bool:
        raise NotImplementedError

    def list(self, namespace: str = "default") -> list[dict[str, Any]]:
        raise NotImplementedError

    def expose(self, deployment: str, port: int, target_port: int, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError
