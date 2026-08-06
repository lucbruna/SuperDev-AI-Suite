"""Digital Twin API package: deterministic HTTP-free API layer."""
from __future__ import annotations

from modules.digital_twin.api.digital_twin_api import DigitalTwinAPI
from modules.digital_twin.api.digital_twin_controllers import TwinControllers
from modules.digital_twin.api.digital_twin_dependencies import TwinDependencies
from modules.digital_twin.api.digital_twin_endpoints import ALL_ENDPOINTS
from modules.digital_twin.api.digital_twin_handlers import TwinHandlers
from modules.digital_twin.api.digital_twin_middleware import (
    MiddlewareChain,
    audit_middleware,
    permission_middleware,
)
from modules.digital_twin.api.digital_twin_responses import ApiResponse
from modules.digital_twin.api.digital_twin_router import TwinRouter
from modules.digital_twin.api.digital_twin_routes import ROUTES, permission_for
from modules.digital_twin.api.digital_twin_serializers import TwinSerializers

__all__ = [
    "ALL_ENDPOINTS",
    "ApiResponse",
    "DigitalTwinAPI",
    "MiddlewareChain",
    "ROUTES",
    "TwinControllers",
    "TwinDependencies",
    "TwinHandlers",
    "TwinRouter",
    "TwinSerializers",
    "audit_middleware",
    "permission_for",
    "permission_middleware",
]
