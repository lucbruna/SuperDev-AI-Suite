from __future__ import annotations

import logging
from typing import Any

from ..integration_models import APIEndpoint


class ApiRegistry:
    """Registry of registered API endpoints, keyed by method+path."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.api.registry")
        self._endpoints: dict[str, APIEndpoint] = {}

    def _key(self, method: str, path: str) -> str:
        return f"{method.upper()} {path}"

    def register(self, endpoint: APIEndpoint) -> str:
        key = self._key(endpoint.method, endpoint.path)
        self._endpoints[key] = endpoint
        return key

    def get(self, method: str, path: str) -> APIEndpoint | None:
        return self._endpoints.get(self._key(method, path))

    def list(self) -> list[APIEndpoint]:
        return list(self._endpoints.values())

    def remove(self, method: str, path: str) -> bool:
        return self._endpoints.pop(self._key(method, path), None) is not None

    def clear(self) -> None:
        self._endpoints.clear()

    def count(self) -> int:
        return len(self._endpoints)

    def snapshot(self) -> dict[str, int]:
        return {"endpoints": len(self._endpoints)}
