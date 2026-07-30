from __future__ import annotations

from .api_config import APIConfigManager
from .api_constants import (
    API_DESCRIPTION,
    API_NAME,
    API_PREFIX,
    API_VERSION,
    RESERVED_ROUTES,
    SUPPORTED_PROTOCOLS,
    SUPPORTED_SERIALIZERS,
)
from .api_context import APIContext
from .api_events import APIEventBus, APIEventType
from .api_factory import APIFactory
from .api_health import APIHealth
from .api_interfaces import (
    IAPIApplication,
    IAPIAuthenticator,
    IAPIAuthorizer,
    IAPICache,
    IAPIGateway,
    IAPILogger,
    IAPIMetrics,
    IAPIMiddleware,
    IAPIRateLimiter,
    IAPIRouter,
    IAPISerializer,
    IAPIServer,
    IAPIValidator,
)
from .api_logger import APILogger
from .api_manager import APIManager
from .api_metrics import APIMetrics
from .api_models import (
    APIConfig,
    APIEndpoint,
    APIError,
    APIMetrics as APIMetricsModel,
    APIRequest,
    APIResponse,
    APIStatus,
    ContentType,
    HTTPMethod,
    PaginatedResponse,
    PaginationParams,
)
from .api_permissions import APIPermissions
from .api_protocols import APIEvent, APIInterceptor
from .api_registry import APIRegistry
from .api_repository import APIRepository
from .api_router import APIRouter
from .api_runtime import APIRuntime
from .api_security import APISecurity
from .api_version import APIVersion
from .application import APIEngine
from .app import APIApplication
from .server import APIServer
from .shutdown import APIShutdown
from .startup import APIStartup

# Phase 3: Pipeline
from .middleware import CORSMiddleware, LoggingMiddleware, RateLimitMiddleware, RequestIDMiddleware
from .validators import JSONSchemaValidator, TypeValidator
from .serializers import JSONSerializer, XMLSerializer, YAMLSerializer, CSVSerializer
from .monitoring import Monitor, HealthChecker, Tracer
from .openapi import OpenAPISpec, OpenAPIGenerator
from .gateway import APIGateway, GatewayRouter
from .mcp import MCPServer, MCPHandler, MCPProtocol

# Phase 4: Routes, Events, Webhooks, SDK
from .routes import RouteRegistry, RouteBuilder, RouteMiddleware
from .events import EventBus, EventDispatcher, EventStore, CallbackManager
from .webhooks import WebhookManager, WebhookDispatcher, WebhookSecurity, WebhookStore
from .sdk import (
    BaseClient,
    RESTClient,
    WebSocketClient,
    GraphQLClient,
    GrpcClient,
    AuthClient,
)

__all__ = [
    "APIApplication",
    "APIConfig",
    "APIConfigManager",
    "APIContext",
    "APIEngine",
    "APIEndpoint",
    "APIError",
    "APIEventBus",
    "APIEventType",
    "APIFactory",
    "APIHealth",
    "APILogger",
    "APIManager",
    "APIMetrics",
    "APIMetricsModel",
    "APIPermissions",
    "APIEvent",
    "APIInterceptor",
    "APIRegistry",
    "APIRepository",
    "APIRouter",
    "APIRuntime",
    "APISecurity",
    "APIServer",
    "APIShutdown",
    "APIStartup",
    "APIStatus",
    "APIVersion",
    "ContentType",
    "HTTPMethod",
    "IAPIApplication",
    "IAPIAuthenticator",
    "IAPIAuthorizer",
    "IAPICache",
    "IAPIGateway",
    "IAPILogger",
    "IAPIMetrics",
    "IAPIMiddleware",
    "IAPIRateLimiter",
    "IAPIRouter",
    "IAPISerializer",
    "IAPIServer",
    "IAPIValidator",
    "PaginatedResponse",
    "PaginationParams",
    "API_DESCRIPTION",
    "API_NAME",
    "API_PREFIX",
    "API_VERSION",
    "RESERVED_ROUTES",
    "SUPPORTED_PROTOCOLS",
    "SUPPORTED_SERIALIZERS",
    # Pipeline
    "CORSMiddleware",
    "LoggingMiddleware",
    "RateLimitMiddleware",
    "RequestIDMiddleware",
    "JSONSchemaValidator",
    "TypeValidator",
    "JSONSerializer",
    "XMLSerializer",
    "YAMLSerializer",
    "CSVSerializer",
    "Monitor",
    "HealthChecker",
    "Tracer",
    "OpenAPISpec",
    "OpenAPIGenerator",
    "APIGateway",
    "GatewayRouter",
    "MCPServer",
    "MCPHandler",
    "MCPProtocol",
    # Routes
    "RouteRegistry",
    "RouteBuilder",
    "RouteMiddleware",
    # Events
    "EventBus",
    "EventDispatcher",
    "EventStore",
    "CallbackManager",
    # Webhooks
    "WebhookManager",
    "WebhookDispatcher",
    "WebhookSecurity",
    "WebhookStore",
    # SDK
    "BaseClient",
    "RESTClient",
    "WebSocketClient",
    "GraphQLClient",
    "GrpcClient",
    "AuthClient",
]
