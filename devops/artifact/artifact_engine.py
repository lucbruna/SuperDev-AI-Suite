from __future__ import annotations

import logging
from typing import Any

from ..devops_context import DevOpsContext


class ArtifactEngine:
    """Manages build artifacts across their lifecycle."""

    def __init__(self, context: DevOpsContext | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.artifact")
        self._context = context

    def publish(self, name: str, version: str, path: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def download(self, name: str, version: str, destination: str) -> dict[str, Any]:
        raise NotImplementedError

    def list(self, name: str | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    def delete(self, name: str, version: str) -> bool:
        raise NotImplementedError

    def promote(self, name: str, version: str, stage: str) -> dict[str, Any]:
        raise NotImplementedError

    def verify(self, name: str, version: str) -> dict[str, Any]:
        raise NotImplementedError
