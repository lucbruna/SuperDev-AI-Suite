from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .docker_engine import DockerEngine


class ContainerManager:
    """Manages Docker containers — run, stop, inspect, logs."""

    def __init__(self, engine: DockerEngine) -> None:
        self._log = logging.getLogger("superdev.devops.docker.containers")
        self._engine = engine

    def run(self, image: str, name: str | None = None, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def stop(self, container_id: str) -> bool:
        raise NotImplementedError

    def start(self, container_id: str) -> bool:
        raise NotImplementedError

    def remove(self, container_id: str) -> bool:
        raise NotImplementedError

    def logs(self, container_id: str, tail: int = 100) -> list[str]:
        raise NotImplementedError

    def inspect(self, container_id: str) -> dict[str, Any]:
        raise NotImplementedError
