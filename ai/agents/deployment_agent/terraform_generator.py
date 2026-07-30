from __future__ import annotations

from typing import Any


class TerraformGenerator:
    """Generates Terraform configuration."""

    def __init__(self) -> None:
        self._providers: list[dict[str, Any]] = []
        self._resources: dict[str, dict[str, Any]] = {}

    def add_provider(self, name: str, config: dict[str, Any]) -> str:
        self._providers.append({"name": name, "config": config})
        return name

    def add_resource(self, resource_type: str, name: str, config: dict[str, Any]) -> str:
        key = f"{resource_type}.{name}"
        self._resources[key] = {"type": resource_type, "name": name, "config": config}
        return key

    def get_resource(self, resource_type: str, name: str) -> dict[str, Any] | None:
        return self._resources.get(f"{resource_type}.{name}")

    @property
    def resource_count(self) -> int:
        return len(self._resources)

    def generate(self) -> str:
        lines: list[str] = ["# Terraform Configuration", ""]
        for prov in self._providers:
            lines.append(f'provider "{prov["name"]}" {{')
            for k, v in prov["config"].items():
                lines.append(f"  {k} = {repr(v)}")
            lines.append("}")
            lines.append("")
        for res in self._resources.values():
            lines.append(f'resource "{res["type"]}" "{res["name"]}" {{')
            for k, v in res["config"].items():
                lines.append(f"  {k} = {repr(v)}")
            lines.append("}")
            lines.append("")
        return "\n".join(lines).strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "providers": self._providers,
            "resources": list(self._resources.values()),
            "resource_count": self.resource_count,
        }
