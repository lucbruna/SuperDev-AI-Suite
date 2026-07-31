from __future__ import annotations

import logging
from typing import Any


class ArtifactBuilder:
    """Builds artifacts from source and configuration."""

    def __init__(self, name: str) -> None:
        self._log = logging.getLogger("superdev.devops.artifact.builder")
        self.name = name
        self._steps: list[dict[str, Any]] = []

    def add_step(self, action: str, **kwargs: Any) -> ArtifactBuilder:
        raise NotImplementedError

    def build(self, version: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def fingerprint(self) -> str:
        raise NotImplementedError

    def cache(self, key: str, data: Any) -> bool:
        raise NotImplementedError
