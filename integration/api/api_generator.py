from __future__ import annotations

import logging
from typing import Any

from ..integration_models import APIEndpoint, IntegrationDefinition


class ApiGenerator:
    """Generates API specifications and endpoint sets from integration definitions."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.api.generator")

    def generate(self, definition: IntegrationDefinition,
                 operations: list[str], base_path: str = "/v1") -> list[APIEndpoint]:
        """Generates endpoints from an integration definition and operations."""
        path = base_path.rstrip("/")
        endpoints: list[APIEndpoint] = []
        for operation in operations:
            endpoints.append(
                APIEndpoint(
                    method="POST",
                    path=f"{path}/{definition.integration_id}/{operation.replace('_', '-')}",
                    operation=operation,
                    version=definition.version,
                    description=f"{definition.name}: {operation}",
                    metadata={"integration_id": definition.integration_id,
                              "provider": definition.provider},
                )
            )
        return endpoints

    def openapi(self, endpoints: list[APIEndpoint], title: str = "SuperDev Integration API",
                version: str = "v1") -> dict[str, Any]:
        """Generates an OpenAPI-style document from endpoints."""
        paths: dict[str, Any] = {}
        for endpoint in endpoints:
            paths.setdefault(endpoint.path, {})[endpoint.method.lower()] = {
                "operationId": endpoint.operation,
                "description": endpoint.description,
                "security": [{"apiKey": []}] if endpoint.auth_required else [],
                "responses": {"200": {"description": "Successful response"}},
            }
        return {
            "openapi": "3.0.0",
            "info": {"title": title, "version": version},
            "paths": paths,
        }
