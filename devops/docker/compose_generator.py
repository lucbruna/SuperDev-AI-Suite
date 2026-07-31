from __future__ import annotations

import logging
from typing import Any


class ComposeGenerator:
    """Generates docker-compose.yml files from service definitions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.docker.compose")

    def generate(self, services: dict[str, Any], version: str = "3.9") -> str:
        raise NotImplementedError

    def validate(self, content: str) -> list[str]:
        raise NotImplementedError

    def to_yaml(self, config: dict[str, Any]) -> str:
        raise NotImplementedError
