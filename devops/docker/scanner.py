from __future__ import annotations

import logging
from typing import Any


class ContainerScanner:
    """Security scanner for Docker images and containers."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.docker.scanner")

    def scan_image(self, image: str) -> dict[str, Any]:
        raise NotImplementedError

    def scan_container(self, container_id: str) -> dict[str, Any]:
        raise NotImplementedError

    def check_secrets(self, path: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    def generate_report(self, scan_id: str) -> str:
        raise NotImplementedError
