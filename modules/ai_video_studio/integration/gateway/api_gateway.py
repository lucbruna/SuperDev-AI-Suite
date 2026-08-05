"""API Gateway — central routing facade for studio APIs."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.gateway.event_gateway import get_event_gateway
from modules.ai_video_studio.integration.gateway.grpc_gateway import get_grpc_gateway
from modules.ai_video_studio.integration.gateway.rest_gateway import get_rest_gateway
from modules.ai_video_studio.integration.gateway.websocket_gateway import (
    get_websocket_gateway,
)


class APIGateway(DomainConnector):
    """REST, WebSocket, gRPC and event gateways."""

    domain = "gateway"
    description = "REST, WebSocket, gRPC and event gateways"

    def __init__(self) -> None:
        super().__init__()
        self._register("register_route", self._route)
        self._register("register_socket", self._socket)
        self._register("register_grpc", self._grpc)
        self._register("publish_event", lambda d: get_event_gateway().publish(
            d.get("event", "gateway.event"), d.get("payload")))
        self._register("status", self._status)

    def _route(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_rest_gateway().register(data.get("method", "GET"), data.get("path", "/"))

    def _socket(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_websocket_gateway().register(data.get("channel", "studio"))

    def _grpc(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_grpc_gateway().register(data.get("service", "VideoStudio"))

    def _status(self, data: dict[str, Any]) -> dict[str, Any]:
        return {
            "rest": get_rest_gateway().routes(),
            "websocket": get_websocket_gateway().routes(),
            "grpc": get_grpc_gateway().routes(),
        }


_api_gateway: APIGateway | None = None


def get_api_gateway() -> APIGateway:
    global _api_gateway
    if _api_gateway is None:
        _api_gateway = APIGateway()
    return _api_gateway
