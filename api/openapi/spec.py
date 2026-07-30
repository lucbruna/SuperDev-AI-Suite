from __future__ import annotations

from typing import Any

from ..api_constants import API_DESCRIPTION, API_NAME, API_VERSION


class OpenAPISpec:
    """Builds and stores OpenAPI specification components."""

    def __init__(self) -> None:
        self._info: dict[str, Any] = {
            "title": API_NAME,
            "version": API_VERSION,
            "description": API_DESCRIPTION,
        }
        self._servers: list[dict[str, Any]] = [{"url": "/", "description": "Local server"}]
        self._paths: dict[str, Any] = {}
        self._components: dict[str, Any] = {"schemas": {}, "securitySchemes": {}}
        self._tags: list[dict[str, Any]] = []

    def set_info(self, title: str, version: str, description: str = "") -> None:
        self._info = {"title": title, "version": version}
        if description:
            self._info["description"] = description

    def add_server(self, url: str, description: str = "") -> None:
        self._servers.append({"url": url, "description": description})

    def add_path(
        self,
        path: str,
        method: str,
        operation: dict[str, Any],
    ) -> None:
        method = method.lower()
        if path not in self._paths:
            self._paths[path] = {}
        self._paths[path][method] = operation

    def add_schema(self, name: str, schema: dict[str, Any]) -> None:
        self._components["schemas"][name] = schema

    def add_security_scheme(self, name: str, scheme: dict[str, Any]) -> None:
        self._components["securitySchemes"][name] = scheme

    def add_tag(self, name: str, description: str = "") -> None:
        self._tags.append({"name": name, "description": description})

    def add_default_security_schemes(self) -> None:
        self.add_security_scheme("BearerAuth", {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        })
        self.add_security_scheme("ApiKeyAuth", {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
        })

    def build(self) -> dict[str, Any]:
        spec: dict[str, Any] = {
            "openapi": "3.1.0",
            "info": self._info,
            "servers": self._servers,
            "paths": self._paths,
            "components": self._components,
        }
        if self._tags:
            spec["tags"] = self._tags
        return spec

    def to_dict(self) -> dict[str, Any]:
        return self.build()
