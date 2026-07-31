from __future__ import annotations

import logging
from typing import Any


class EnvironmentTemplate:
    """Templates for scaffolding new environments."""

    def __init__(self, name: str) -> None:
        self._log = logging.getLogger("superdev.devops.environments.template")
        self.name = name
        self._blocks: list[dict[str, Any]] = []

    def add_block(self, block_type: str, **kwargs: Any) -> EnvironmentTemplate:
        raise NotImplementedError

    def instantiate(self, environment: str, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError

    def render(self) -> str:
        raise NotImplementedError

    def validate(self) -> list[str]:
        raise NotImplementedError
