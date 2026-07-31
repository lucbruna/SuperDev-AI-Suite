from __future__ import annotations

import logging
from typing import Any

from ..integration_models import APIEndpoint


class ApiDocumentation:
    """Generates human and machine-readable documentation for endpoints."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.api.docs")

    def describe(self, endpoint: APIEndpoint) -> dict[str, Any]:
        return {
            "method": endpoint.method,
            "path": endpoint.path,
            "operation": endpoint.operation,
            "version": endpoint.version,
            "auth_required": endpoint.auth_required,
            "rate_limit": endpoint.rate_limit,
            "description": endpoint.description,
        }

    def describe_all(self, endpoints: list[APIEndpoint]) -> list[dict[str, Any]]:
        return [self.describe(endpoint) for endpoint in endpoints]

    def markdown(self, endpoints: list[APIEndpoint], title: str = "API Reference") -> str:
        lines = [f"# {title}", ""]
        for endpoint in endpoints:
            auth = "🔒" if endpoint.auth_required else ""
            lines.append(f"## {endpoint.method} {endpoint.path} {auth}")
            if endpoint.description:
                lines.append(f"{endpoint.description}")
            lines.append(f"- Operation: `{endpoint.operation}`")
            lines.append(f"- Version: `{endpoint.version}`")
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"
