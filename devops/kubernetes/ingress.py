from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .kubernetes_engine import KubernetesEngine


class IngressManager:
    """Manages Kubernetes Ingress resources."""

    def __init__(self, engine: KubernetesEngine) -> None:
        self._log = logging.getLogger("superdev.devops.kubernetes.ingress")
        self._engine = engine

    def create(self, name: str, host: str, service: str, port: int, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def delete(self, name: str, namespace: str = "default") -> bool:
        raise NotImplementedError

    def list(self, namespace: str = "default") -> list[dict[str, Any]]:
        raise NotImplementedError

    def add_rule(self, name: str, path: str, service: str, port: int) -> dict[str, Any]:
        raise NotImplementedError
