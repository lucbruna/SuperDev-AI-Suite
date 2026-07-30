from __future__ import annotations

from typing import Any

from ..api_constants import API_DESCRIPTION, API_NAME, API_PREFIX, API_VERSION
from ..api_registry import APIRegistry
from .spec import OpenAPISpec


class OpenAPIGenerator:
    """Generates OpenAPI specs from registered API routes."""

    def __init__(self, registry: APIRegistry) -> None:
        self._registry = registry
        self._spec = OpenAPISpec()
        self._spec.add_default_security_schemes()

    def generate(self) -> dict[str, Any]:
        routes = self._registry.list_routes()
        for route in routes:
            method = route.get("method", "GET").lower()
            path = route.get("path", "/")
            handler = route.get("handler", "")
            description = route.get("description", "")
            tags = route.get("tags", ["default"])
            auth_required = route.get("auth_required", True)

            operation: dict[str, Any] = {
                "summary": description or f"{method.upper()} {path}",
                "description": description,
                "tags": tags,
                "responses": {
                    "200": {"description": "Successful response"},
                    "400": {"description": "Bad request"},
                    "500": {"description": "Internal server error"},
                },
            }

            if auth_required:
                operation["security"] = [{"BearerAuth": []}]

            self._spec.add_path(path, method, operation)

        return self._spec.build()

    def add_schema_from_model(self, name: str, model: dict[str, Any]) -> None:
        self._spec.add_schema(name, model)

    def to_dict(self) -> dict[str, Any]:
        return {"generator": "OpenAPIGenerator", "registry_routes": len(self._registry.list_routes())}
