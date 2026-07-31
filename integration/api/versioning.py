from __future__ import annotations

import logging
from typing import Any

from ..integration_models import APIEndpoint


class ApiVersioning:
    """Manages API version resolution and compatibility checks."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.api.versioning")

    def resolve(self, endpoints: list[APIEndpoint], requested: str) -> APIEndpoint | None:
        """Returns the endpoint whose version matches the requested version,
        preferring the closest available version when an exact match is absent.
        """
        for endpoint in endpoints:
            if endpoint.version == requested:
                return endpoint
        return None

    def versions(self, endpoints: list[APIEndpoint]) -> list[str]:
        return sorted({endpoint.version for endpoint in endpoints})

    def latest(self, endpoints: list[APIEndpoint]) -> APIEndpoint | None:
        if not endpoints:
            return None
        versions = {endpoint.version: endpoint for endpoint in endpoints}
        ordered = sorted(versions, key=self._sort_key)
        return versions[ordered[-1]]

    def path_for(self, endpoint: APIEndpoint, version: str) -> str:
        """Rewrites an endpoint path to a specific version, e.g. /v2/orders."""
        parts = [p for p in endpoint.path.split("/") if p]
        if parts and parts[0].startswith("v"):
            parts[0] = version
        else:
            parts.insert(0, version)
        return "/" + "/".join(parts)

    @staticmethod
    def _sort_key(version: str) -> tuple[int, ...]:
        parts = []
        for token in version.lstrip("v").split("."):
            try:
                parts.append(int(token))
            except ValueError:
                parts.append(0)
        return tuple(parts)
