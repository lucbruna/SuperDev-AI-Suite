"""Generator for API documentation."""

from typing import Any

from .models import ApiEndpoint, ApiParameter


class ApiDocGenerator:
    """Generates API documentation from endpoint specifications."""

    def __init__(self):
        self._endpoints: list[ApiEndpoint] = []

    def add_endpoint(self, endpoint: ApiEndpoint) -> None:
        self._endpoints.append(endpoint)

    def generate(self, endpoint_dicts: list[dict[str, Any]] = None) -> str:
        if endpoint_dicts:
            self._endpoints = []
            for ed in endpoint_dicts:
                params = [
                    ApiParameter(
                        name=p.get("name", ""),
                        type=p.get("type", "string"),
                        required=p.get("required", False),
                        description=p.get("description", ""),
                    )
                    for p in ed.get("parameters", [])
                ]
                ep = ApiEndpoint(
                    path=ed.get("path", ""),
                    method=ed.get("method", "GET"),
                    summary=ed.get("summary", ""),
                    description=ed.get("description", ""),
                    parameters=params,
                )
                self._endpoints.append(ep)

        lines = ["# API Reference\n"]
        for ep in self._endpoints:
            lines.append(f"## {ep.method} {ep.path}")
            lines.append(f"\n**Summary:** {ep.summary}\n")
            if ep.description:
                lines.append(f"{ep.description}\n")
            if ep.parameters:
                lines.append("**Parameters:**\n")
                lines.append("| Name | Type | Required | Description |")
                lines.append("|------|------|----------|-------------|")
                for p in ep.parameters:
                    lines.append(f"| {p.name} | {p.type} | {p.required} | {p.description} |")
                lines.append("")
        return "\n".join(lines)

    def get_endpoints(self) -> list[ApiEndpoint]:
        return list(self._endpoints)

    def find_by_tag(self, tag: str) -> list[ApiEndpoint]:
        return [e for e in self._endpoints if tag in e.tags]
