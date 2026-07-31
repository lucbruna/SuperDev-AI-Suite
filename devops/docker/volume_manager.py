from __future__ import annotations

import logging
from typing import Any


class VolumeManager:
    """Manages Docker volumes — create, mount, backup, remove."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.docker.volumes")

    def create(self, name: str, driver: str = "local", **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def remove(self, name: str) -> bool:
        raise NotImplementedError

    def list(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    def backup(self, name: str, dest: str) -> str:
        raise NotImplementedError
