from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HTTPMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    TRACE = "TRACE"


class ContentType(Enum):
    JSON = "application/json"
    XML = "application/xml"
    YAML = "application/x-yaml"
    FORM = "application/x-www-form-urlencoded"
    MULTIPART = "multipart/form-data"
    PLAIN = "text/plain"
    HTML = "text/html"
    CSV = "text/csv"
    MSGPACK = "application/msgpack"
    PROTOBUF = "application/protobuf"
    OCTET = "application/octet-stream"


class APIStatus(Enum):
    RUNNING = "running"
    STOPPED = "stopped"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"
    ERROR = "error"


@dataclass
class APIRequest:
    method: str = "GET"
    path: str = "/"
    headers: dict[str, str] = field(default_factory=dict)
    query: dict[str, list[str]] = field(default_factory=dict)
    body: Any = None
    content_type: str = "application/json"
    client_ip: str = ""
    user_id: str = ""
    request_id: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class APIResponse:
    status_code: int = 200
    body: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    content_type: str = "application/json"
    elapsed_ms: float = 0.0
    request_id: str = ""


@dataclass
class APIError(Exception):
    status_code: int = 500
    message: str = "Internal Server Error"
    code: str = "INTERNAL_ERROR"
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class APIEndpoint:
    method: HTTPMethod = HTTPMethod.GET
    path: str = "/"
    handler: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    auth_required: bool = True
    rate_limit: int = 0


@dataclass
class APIMetrics:
    total_requests: int = 0
    active_connections: int = 0
    avg_latency_ms: float = 0.0
    error_rate: float = 0.0
    requests_per_second: float = 0.0
    uptime_seconds: float = 0.0


@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = field(default_factory=lambda: ["*"])
    rate_limit_default: int = 100
    rate_limit_window: int = 60
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 60
    max_request_size_mb: int = 10
    request_timeout_sec: int = 30
    enable_docs: bool = True
    enable_metrics: bool = True
    enable_tracing: bool = False
    log_level: str = "INFO"
    allowed_hosts: list[str] = field(default_factory=list)
    trusted_proxies: list[str] = field(default_factory=list)


@dataclass
class PaginationParams:
    page: int = 1
    page_size: int = 20
    sort_by: str = "created_at"
    sort_order: str = "desc"


@dataclass
class PaginatedResponse:
    items: list[Any] = field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 1
    has_next: bool = False
    has_prev: bool = False
