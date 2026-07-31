from __future__ import annotations

import logging
from typing import Any


class DockerCleanup:
    """Cleans up unused Docker resources — images, containers, volumes."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.docker.cleanup")

    def prune_images(self, dangling: bool = True) -> dict[str, Any]:
        raise NotImplementedError

    def prune_containers(self, exited: bool = True) -> dict[str, Any]:
        raise NotImplementedError

    def prune_volumes(self) -> dict[str, Any]:
        raise NotImplementedError

    def prune_all(self) -> dict[str, Any]:
        raise NotImplementedError
