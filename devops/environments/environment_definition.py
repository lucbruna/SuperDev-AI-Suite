from __future__ import annotations

import logging
from typing import Any


class EnvironmentDefinition:
    """Declarative environment configuration."""

    def __init__(self, name: str, environment_type: str = "development") -> None:
        self._log = logging.getLogger("superdev.devops.environments.definition")
        self.name = name
        self.environment_type = environment_type
        self._spec: dict[str, Any] = {}

    def from_dict(self, spec: dict[str, Any]) -> EnvironmentDefinition:
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self) -> list[str]:
        raise NotImplementedError

    def merge(self, other: EnvironmentDefinition) -> EnvironmentDefinition:
        raise NotImplementedError
