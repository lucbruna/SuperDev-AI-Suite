from __future__ import annotations

import logging
from typing import Any


class DockerRegistry:
    """Interacts with Docker image registries."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.docker.registry")

    def login(self, registry: str, username: str, password: str) -> bool:
        raise NotImplementedError

    def logout(self, registry: str) -> bool:
        raise NotImplementedError

    def push(self, image: str, registry: str) -> dict[str, Any]:
        raise NotImplementedError

    def pull(self, image: str, registry: str) -> dict[str, Any]:
        raise NotImplementedError
