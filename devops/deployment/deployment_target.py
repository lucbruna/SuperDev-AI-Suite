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
        self._connected = False

    def connect(self) -> bool:
        """Simulate connecting to the target."""
        self._connected = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    @property
    def connected(self) -> bool:
        return self._connected

    def capabilities(self) -> list[str]:
        """Return capabilities supported by the target type."""
        base = ["deploy", "health", "rollback"]
        if self.target_type in ("kubernetes", "k8s", "cluster"):
            base += ["canary", "blue_green", "scaling", "rolling"]
        elif self.target_type in ("cloud", "aws", "gcp", "azure"):
            base += ["provision", "dns"]
        return base

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "target_type": self.target_type,
            "connected": self._connected,
            "capabilities": self.capabilities(),
            "details": dict(self._details),
        }
