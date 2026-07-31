from __future__ import annotations

import logging
from typing import Any


class DeploymentTarget:
    """Represents a deployment target (host, cluster, cloud)."""

    def __init__(self, name: str, target_type: str, **kwargs: Any) -> None:
        self._log = logging.getLogger("superdev.devops.deployment.target")
        self.name = name
        self.target_type = target_type
        self._details: dict[str, Any] = kwargs

    def connect(self) -> bool:
        raise NotImplementedError

    def disconnect(self) -> bool:
        raise NotImplementedError

    def capabilities(self) -> list[str]:
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError
