from __future__ import annotations

from enum import Enum
from typing import Any, Callable


class MethodType(Enum):
    UNARY = "unary"
    SERVER_STREAMING = "server_streaming"
    CLIENT_STREAMING = "client_streaming"
    BIDI_STREAMING = "bidi_streaming"


class MethodDefinition:
    """Defines a single gRPC method."""

    def __init__(
        self,
        name: str,
        handler: Callable,
        request_type: str = "JSON",
        response_type: str = "JSON",
        method_type: MethodType = MethodType.UNARY,
        description: str = "",
    ) -> None:
        self.name = name
        self.handler = handler
        self.request_type = request_type
        self.response_type = response_type
        self.method_type = method_type
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "method_type": self.method_type.value,
            "request_type": self.request_type,
            "response_type": self.response_type,
            "description": self.description,
        }


class ServiceDefinition:
    """Defines a gRPC service with its methods."""

    def __init__(self, name: str, methods: list[MethodDefinition] | None = None) -> None:
        self.name = name
        self._methods: dict[str, MethodDefinition] = {}
        if methods:
            for m in methods:
                self._methods[m.name] = m

    def add_method(self, method: MethodDefinition) -> None:
        self._methods[method.name] = method

    def get_method(self, name: str) -> MethodDefinition | None:
        return self._methods.get(name)

    def list_methods(self) -> list[MethodDefinition]:
        return list(self._methods.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "methods": [m.to_dict() for m in self._methods.values()],
        }


class ServiceRegistry:
    """Registry for gRPC services."""

    def __init__(self) -> None:
        self._services: dict[str, ServiceDefinition] = {}

    def register(self, service: ServiceDefinition) -> None:
        self._services[service.name] = service

    def get(self, name: str) -> ServiceDefinition | None:
        return self._services.get(name)

    def list_services(self) -> list[ServiceDefinition]:
        return list(self._services.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "services": [s.to_dict() for s in self._services.values()],
            "count": len(self._services),
        }
