from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .docker_engine import DockerEngine


class ImageBuilder:
    """Builds Docker images from Dockerfiles or build contexts."""

    def __init__(self, engine: DockerEngine) -> None:
        self._log = logging.getLogger("superdev.devops.docker.image_builder")
        self._engine = engine

    def build(self, path: str, tag: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def build_from_dockerfile(self, dockerfile: str, tag: str, context: str = ".") -> dict[str, Any]:
        raise NotImplementedError

    def cancel(self, build_id: str) -> bool:
        raise NotImplementedError
