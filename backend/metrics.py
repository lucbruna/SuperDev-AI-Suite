from __future__ import annotations

import time

from prometheus_client import Counter, Gauge, Histogram
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

request_counter = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=["method", "endpoint", "status"],
)

request_duration = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    labelnames=["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

active_connections = Gauge(
    "http_active_connections",
    "Number of active HTTP connections",
)

error_counter = Counter(
    "http_errors_total",
    "Total HTTP errors",
    labelnames=["method", "endpoint", "status"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, exclude_paths: list[str] | None = None) -> None:
        super().__init__(app)
        self._exclude_paths = exclude_paths or ["/metrics", "/health"]

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self._exclude_paths):
            return await call_next(request)

        method = request.method
        active_connections.inc()

        start = time.monotonic()
        try:
            response = await call_next(request)
            return response
        finally:
            duration = time.monotonic() - start
            status = response.status_code if "response" in dir() else 500

            request_counter.labels(method=method, endpoint=path, status=status).inc()
            request_duration.labels(method=method, endpoint=path).observe(duration)
            active_connections.dec()

            if status >= 400:
                error_counter.labels(method=method, endpoint=path, status=status).inc()