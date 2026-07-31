from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .kubernetes_engine import KubernetesEngine


class HelmManager:
    """Manages Helm charts and releases."""

    def __init__(self, engine: KubernetesEngine) -> None:
        self._log = logging.getLogger("superdev.devops.kubernetes.helm")
        self._engine = engine

    def install(self, release: str, chart: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def upgrade(self, release: str, chart: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def uninstall(self, release: str, namespace: str = "default") -> bool:
        raise NotImplementedError

    def list(self, namespace: str = "default") -> list[dict[str, Any]]:
        raise NotImplementedError

    def create_chart(self, name: str, dest: str = ".") -> str:
        raise NotImplementedError
