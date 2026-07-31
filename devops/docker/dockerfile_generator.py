from __future__ import annotations

import logging
from typing import Any


class DockerfileGenerator:
    """Generates optimized Dockerfile content from project config."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.devops.docker.dockerfile")

    def generate(self, config: dict[str, Any]) -> str:
        raise NotImplementedError

    def from_template(self, template: str, config: dict[str, Any]) -> str:
        raise NotImplementedError

    def validate(self, content: str) -> list[str]:
        raise NotImplementedError
