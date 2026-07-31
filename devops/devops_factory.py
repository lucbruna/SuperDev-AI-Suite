from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .devops_engine import DevOpsEngine


class DevOpsFactory:
    """Factory for creating DevOps resources and services."""

    def __init__(self, engine: DevOpsEngine) -> None:
        self._engine = engine

    def create_service(self, name: str, service_type: str, config: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError

    def create_resource(self, name: str, resource_type: str, config: dict[str, Any] | None = None) -> Any:
        raise NotImplementedError
