from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .docker_engine import DockerEngine


class ImageManager:
    """Manages Docker images — pull, push, tag, prune."""

    def __init__(self, engine: DockerEngine) -> None:
        self._log = logging.getLogger("superdev.devops.docker.images")
        self._engine = engine

    def pull(self, image: str) -> dict[str, Any]:
        raise NotImplementedError

    def push(self, image: str, registry: str | None = None) -> dict[str, Any]:
        raise NotImplementedError

    def tag(self, image: str, tag: str) -> bool:
        raise NotImplementedError

    def remove(self, image: str) -> bool:
        raise NotImplementedError

    def list(self) -> list[dict[str, Any]]:
        raise NotImplementedError
