from __future__ import annotations

import logging
from typing import Any

from .container_manager import ContainerManager
from .image_builder import ImageBuilder
from .image_manager import ImageManager


class DockerEngine:
    """Central engine for Docker container management."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.docker")
        self.images = ImageManager(self)
        self.containers = ContainerManager(self)
        self.builder = ImageBuilder(self)

    def build(self, path: str, tag: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def run(self, image: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def stop(self, container_id: str) -> bool:
        raise NotImplementedError

    def list_containers(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def list_images(self) -> list[dict[str, Any]]:
        raise NotImplementedError
