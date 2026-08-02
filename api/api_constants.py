from __future__ import annotations

from .api_models import HTTPMethod

API_VERSION = "1.0.0"
API_NAME = "SuperDev API Engine"
API_DESCRIPTION = "Enterprise API Engine for SuperDev AI Suite"
API_PREFIX = "/api/v1"
DOCS_URL = "/docs"
OPENAPI_URL = "/openapi.json"
REDOC_URL = "/redoc"

HEALTH_ENDPOINT = "/health"
READINESS_ENDPOINT = "/ready"
LIVENESS_ENDPOINT = "/live"
METRICS_ENDPOINT = "/metrics"

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
DEFAULT_TIMEOUT_SEC = 30
MAX_REQUEST_SIZE_MB = 10

CORS_DEFAULT_ORIGINS: list[str] = []  # explicit origins required; never '*' with credentials
CORS_ALLOW_METHODS: list[str] = [m.value for m in HTTPMethod]
CORS_ALLOW_HEADERS: list[str] = [
    "Authorization",
    "Content-Type",
    "X-Request-ID",
    "X-API-Key",
    "X-CSRF-Token",
]
CORS_EXPOSE_HEADERS: list[str] = [
    "X-Request-ID",
    "X-RateLimit-Limit",
    "X-RateLimit-Remaining",
    "X-RateLimit-Reset",
]

RESERVED_ROUTES: set[str] = {
    "/health", "/ready", "/live", "/metrics",
    "/docs", "/redoc", "/openapi.json",
    "/api/v1",
}

CONTENT_TYPES: dict[str, str] = {
    "json": "application/json",
    "xml": "application/xml",
    "yaml": "application/x-yaml",
    "csv": "text/csv",
    "msgpack": "application/msgpack",
    "protobuf": "application/protobuf",
    "form": "application/x-www-form-urlencoded",
    "html": "text/html",
    "plain": "text/plain",
}

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"
API_KEY_HEADER = "X-API-Key"
AUTHORIZATION_HEADER = "Authorization"
FORWARDED_FOR_HEADER = "X-Forwarded-For"
USER_AGENT_HEADER = "User-Agent"

RATE_LIMIT_HEADERS = {
    "limit": "X-RateLimit-Limit",
    "remaining": "X-RateLimit-Remaining",
    "reset": "X-RateLimit-Reset",
}

SUPPORTED_SERIALIZERS = ["json", "xml", "yaml", "csv", "msgpack", "protobuf"]
SUPPORTED_PROTOCOLS = ["rest", "websocket", "graphql", "grpc"]
