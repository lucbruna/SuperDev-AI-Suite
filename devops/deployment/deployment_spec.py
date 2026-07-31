from __future__ import annotations

import logging
from typing import Any


class DeploymentSpec:
    """Defines a deployment specification."""

    def __init__(self, service: str, version: str) -> None:
        self._log = logging.getLogger("superdev.devops.deployment.spec")
        self.service = service
        self.version = version
        self._spec: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> "DeploymentSpec":
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError

    def validate(self) -> list[str]:
        raise NotImplementedError
