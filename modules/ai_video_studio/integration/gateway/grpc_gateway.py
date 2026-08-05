"""gRPC Gateway — service/method registration (proto-aware, no live server)."""
from __future__ import annotations

from typing import Any


class GRPCGateway:
    """Registers gRPC services and their methods."""

    def __init__(self) -> None:
        self._services: dict[str, dict[str, Any]] = {}

    def register(self, service: str, *, methods: list[str] | None = None) -> dict[str, Any]:
        methods = methods or ["GenerateVideo", "RenderJob", "ExportMedia"]
        self._services[service] = {"service": service, "methods": list(methods)}
        return {"registered": service}

    def routes(self) -> dict[str, Any]:
        return {"services": list(self._services.values()), "count": len(self._services)}


_grpc_gateway: GRPCGateway | None = None


def get_grpc_gateway() -> GRPCGateway:
    global _grpc_gateway
    if _grpc_gateway is None:
        _grpc_gateway = GRPCGateway()
    return _grpc_gateway
