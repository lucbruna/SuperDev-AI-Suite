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
        handler: Callable | None = None,
        input_type: str = "",
        output_type: str = "",
        request_type: str = "JSON",
        response_type: str = "JSON",
        method_type: MethodType = MethodType.UNARY,
        description: str = "",
    ) -> None:
        self.name = name
        self.handler = handler
        self.input_type = input_type
        self.output_type = output_type
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

    def register_service(self, name: str) -> None:
        if name not in self._services:
            self._services[name] = ServiceDefinition(name)

    def register_method(self, service_name: str, method: MethodDefinition) -> None:
        if service_name not in self._services:
            self._services[service_name] = ServiceDefinition(service_name)
        self._services[service_name].add_method(method)

    def get_methods(self, service_name: str) -> list[MethodDefinition]:
        service = self._services.get(service_name)
        return service.list_methods() if service else []

    def get(self, name: str) -> ServiceDefinition | None:
        return self._services.get(name)

    def list_services(self) -> list[str]:
        return list(self._services.keys())

    def to_dict(self) -> dict[str, Any]:
        return {
            "services": [s.to_dict() for s in self._services.values()],
            "count": len(self._services),
        }
