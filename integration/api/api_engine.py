from __future__ import annotations

import logging
from typing import Any

from ..integration_models import APIEndpoint
from .api_builder import ApiBuilder
from .api_generator import ApiGenerator
from .api_registry import ApiRegistry
from .documentation import ApiDocumentation
from .endpoint_manager import EndpointManager
from .schema_manager import SchemaManager
from .versioning import ApiVersioning


class ApiEngine:
    """Facade for API management: build, register, document, and version endpoints."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.api")
        self.builder = ApiBuilder()
        self.generator = ApiGenerator()
        self.registry = ApiRegistry()
        self.endpoints = EndpointManager()
        self.schemas = SchemaManager()
        self.docs = ApiDocumentation()
        self.versioning = ApiVersioning()

    def register(self, endpoint: APIEndpoint) -> str:
        key = self.registry.register(endpoint)
        self.endpoints.create(
            method=endpoint.method,
            path=endpoint.path,
            operation=endpoint.operation,
            version=endpoint.version,
            auth_required=endpoint.auth_required,
            rate_limit=endpoint.rate_limit,
            description=endpoint.description,
        )
        return key

    def register_spec(self, spec: dict[str, Any]) -> APIEndpoint:
        endpoint = self.builder.build(spec)
        self.register(endpoint)
        return endpoint

    def get(self, method: str, path: str) -> APIEndpoint | None:
        return self.registry.get(method, path)

    def list(self, version: str | None = None) -> list[APIEndpoint]:
        return self.endpoints.list(version)

    def remove(self, method: str, path: str) -> bool:
        removed = self.registry.remove(method, path)
        self.endpoints.delete(method, path)
        return removed

    def register_schema(self, name: str, schema: dict[str, Any]) -> None:
        self.schemas.register(name, schema)

    def validate(self, schema_name: str, payload: Any) -> bool:
        return self.schemas.validate(schema_name, payload)

    def openapi(self, title: str = "SuperDev Integration API") -> dict[str, Any]:
        return self.generator.openapi(self.list(), title=title)

    def markdown_docs(self) -> str:
        return self.docs.markdown(self.list())

    def stats(self) -> dict[str, int]:
        return {
            "endpoints": self.registry.count(),
            "schemas": len(self.schemas.list()),
        }
