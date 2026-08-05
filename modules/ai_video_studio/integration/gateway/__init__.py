"""Gateway — REST, WebSocket, gRPC and event gateways."""
from modules.ai_video_studio.integration.gateway.api_gateway import (
    APIGateway,
    get_api_gateway,
)
from modules.ai_video_studio.integration.gateway.rest_gateway import (
    RESTGateway,
    get_rest_gateway,
)
from modules.ai_video_studio.integration.gateway.websocket_gateway import (
    WebSocketGateway,
    get_websocket_gateway,
)

__all__ = [
    "APIGateway",
    "get_api_gateway",
    "RESTGateway",
    "get_rest_gateway",
    "WebSocketGateway",
    "get_websocket_gateway",
]
