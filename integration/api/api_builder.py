from __future__ import annotations

import logging
from typing import Any

from ..integration_models import APIEndpoint


class ApiBuilder:
    """Builds API endpoints from declarative specifications."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.api.builder")

    def build(self, spec: dict[str, Any]) -> APIEndpoint:
        """Builds an endpoint from a spec dict.

        Expected keys: method, path, operation, version, auth_required,
        rate_limit, description.
        """
        if "method" not in spec or "path" not in spec or "operation" not in spec:
            raise ValueError("spec requires method, path, and operation")
        return APIEndpoint(
            method=str(spec["method"]).upper(),
            path=str(spec["path"]),
            operation=str(spec["operation"]),
            version=str(spec.get("version", "v1")),
            auth_required=bool(spec.get("auth_required", True)),
            rate_limit=int(spec.get("rate_limit", 0)),
            description=str(spec.get("description", "")),
            metadata=dict(spec.get("metadata", {})),
        )

    def build_many(self, specs: list[dict[str, Any]]) -> list[APIEndpoint]:
        return [self.build(spec) for spec in specs]

    def from_connector(self, connector_type: str, operations: list[str],
                       base_path: str = "/") -> list[APIEndpoint]:
        """Generates REST endpoints for connector operations."""
        path = base_path.rstrip("/") if base_path != "/" else ""
        endpoints: list[APIEndpoint] = []
        for operation in operations:
            endpoint_path = f"{path}/{operation.replace('_', '-')}"
            endpoints.append(
                APIEndpoint(
                    method="POST",
                    path=endpoint_path,
                    operation=operation,
                    description=f"{connector_type} operation {operation}",
                )
            )
        return endpoints
