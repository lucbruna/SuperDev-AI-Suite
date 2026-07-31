from __future__ import annotations

import logging
from typing import Any

from ..integration_models import APIEndpoint


class EndpointManager:
    """CRUD management for API endpoints."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.api.endpoints")
        self._endpoints: dict[str, APIEndpoint] = {}
        self._routes: dict[str, dict[str, Any]] = {}  # key -> routing info

    def _key(self, method: str, path: str) -> str:
        return f"{method.upper()} {path}"

    def create(self, method: str, path: str, operation: str,
               version: str = "v1", auth_required: bool = True,
               rate_limit: int = 0, description: str = "") -> APIEndpoint:
        endpoint = APIEndpoint(
            method=method.upper(),
            path=path,
            operation=operation,
            version=version,
            auth_required=auth_required,
            rate_limit=rate_limit,
            description=description,
        )
        self._endpoints[self._key(endpoint.method, endpoint.path)] = endpoint
        return endpoint

    def update(self, endpoint: APIEndpoint) -> bool:
        key = self._key(endpoint.method, endpoint.path)
        if key not in self._endpoints:
            return False
        self._endpoints[key] = endpoint
        return True

    def delete(self, method: str, path: str) -> bool:
        return self._endpoints.pop(self._key(method, path), None) is not None

    def get(self, method: str, path: str) -> APIEndpoint | None:
        return self._endpoints.get(self._key(method, path))

    def list(self, version: str | None = None) -> list[APIEndpoint]:
        endpoints = self._endpoints.values()
        if version:
            endpoints = [e for e in endpoints if e.version == version]
        return list(endpoints)

    def bind(self, method: str, path: str, connection_id: str, operation: str) -> None:
        """Binds an endpoint to a connection operation for gateway routing."""
        self._routes[self._key(method, path)] = {
            "connection_id": connection_id,
            "operation": operation,
        }

    def route_for(self, method: str, path: str) -> dict[str, Any] | None:
        return self._routes.get(self._key(method, path))

    def count(self) -> int:
        return len(self._endpoints)
