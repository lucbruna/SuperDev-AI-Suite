"""Request body size limit middleware."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject requests with body larger than max_body_size bytes."""

    def __init__(self, app, max_body_size: int = 10 * 1024 * 1024) -> None:
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_body_size:
            return JSONResponse(
                status_code=413,
                content={"detail": f"Request body too large (max {self.max_body_size} bytes)"},
            )
        return await call_next(request)
