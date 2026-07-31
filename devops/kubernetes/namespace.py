from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .kubernetes_engine import KubernetesEngine


class NamespaceManager:
    """Manages Kubernetes namespaces."""

    def __init__(self, engine: KubernetesEngine) -> None:
        self._log = logging.getLogger("superdev.devops.kubernetes.namespaces")
        self._engine = engine

    def create(self, name: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def delete(self, name: str) -> bool:
        raise NotImplementedError

    def list(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def exists(self, name: str) -> bool:
        raise NotImplementedError
