from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .devops_models import DevOpsService

if TYPE_CHECKING:
    from .devops_engine import DevOpsEngine


class DevOpsFactory:
    """Factory for creating DevOps resources and services."""

    def __init__(self, engine: DevOpsEngine) -> None:
        self._engine = engine

    def create_service(self, name: str, service_type: str, config: dict[str, Any] | None = None) -> Any:
        """Create and register a DevOpsService in the engine registry."""
        config = config or {}
        service = DevOpsService(
            name=name,
            service_type=service_type,
            version=config.get("version", "latest"),
            environment=config.get("environment", self._engine.config.environment),
            config=config,
            status=config.get("status", "created"),
            endpoints=list(config.get("endpoints", [])),
        )
        self._engine.registry.register_service(name, service)
        return service

    def create_resource(self, name: str, resource_type: str, config: dict[str, Any] | None = None) -> Any:
        """Create and register a resource in the engine registry."""
        config = config or {}
        resource = {
            "name": name,
            "resource_type": resource_type,
            "provider": config.get("provider", self._engine.config.provider),
            "region": config.get("region", self._engine.config.region),
            "config": config,
            "status": "created",
        }
        self._engine.registry.register_resource(name, resource)
        return resource
