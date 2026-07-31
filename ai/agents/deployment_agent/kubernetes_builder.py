from __future__ import annotations

from typing import Any


class KubernetesBuilder:
    """Generates Kubernetes deployment and service manifests."""

    def __init__(self) -> None:
        self._deployments: dict[str, dict[str, Any]] = {}
        self._services: dict[str, dict[str, Any]] = {}

    def add_deployment(self, name: str, image: str, replicas: int = 1) -> str:
        self._deployments[name] = {"name": name, "image": image, "replicas": replicas}
        return name

    def get_deployment(self, name: str) -> dict[str, Any] | None:
        return self._deployments.get(name)

    @property
    def deployment_count(self) -> int:
        return len(self._deployments)

    def add_service(self, name: str, port: int, target_port: int | None = None) -> str:
        self._services[name] = {"name": name, "port": port, "target_port": target_port or port}
        return name

    @property
    def service_count(self) -> int:
        return len(self._services)

    def generate(self) -> str:
        lines: list[str] = ["# Kubernetes Manifests", ""]
        for dep in self._deployments.values():
            lines.append("---")
            lines.append("apiVersion: apps/v1")
            lines.append("kind: Deployment")
            lines.append("metadata:")
            lines.append(f"  name: {dep['name']}")
            lines.append("spec:")
            lines.append(f"  replicas: {dep['replicas']}")
            lines.append("  template:")
            lines.append("    spec:")
            lines.append("      containers:")
            lines.append(f"      - name: {dep['name']}")
            lines.append(f"        image: {dep['image']}")
            lines.append("")
        for svc in self._services.values():
            lines.append("---")
            lines.append("apiVersion: v1")
            lines.append("kind: Service")
            lines.append("metadata:")
            lines.append(f"  name: {svc['name']}")
            lines.append("spec:")
            lines.append("  ports:")
            lines.append(f"  - port: {svc['port']}")
            lines.append(f"    targetPort: {svc['target_port']}")
            lines.append("")
        return "\n".join(lines).strip()

    def to_dict(self) -> dict[str, Any]:
        return {
            "deployments": list(self._deployments.values()),
            "services": list(self._services.values()),
            "deployment_count": self.deployment_count,
        }
