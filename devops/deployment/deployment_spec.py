from __future__ import annotations

import logging
from typing import Any


class DeploymentSpec:
    """Defines and validates a deployment specification."""

    def __init__(self, service: str, version: str) -> None:
        self._log = logging.getLogger("superdev.devops.deployment.spec")
        self.service = service
        self.version = version
        self._spec: dict[str, Any] = {}

    def set(self, key: str, value: Any) -> DeploymentSpec:
        """Set a spec field (chainable)."""
        self._spec[key] = value
        return self

    def get(self, key: str, default: Any = None) -> Any:
        return self._spec.get(key, default)

    def to_dict(self) -> dict[str, Any]:
        return {
            "service": self.service,
            "version": self.version,
            "spec": dict(self._spec),
        }

    def validate(self) -> list[str]:
        """Return a list of spec validation errors (empty when valid)."""
        errors: list[str] = []
        if not self.service or not self.service.strip():
            errors.append("service is required")
        if not self.version or not self.version.strip():
            errors.append("version is required")
        instances = self._spec.get("instances")
        if instances is not None and (not isinstance(instances, int) or instances < 1):
            errors.append("instances must be a positive integer")
        return errors
