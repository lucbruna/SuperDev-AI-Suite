"""Request ID middleware — propagates X-Request-ID through the request lifecycle."""

from __future__ import annotations

import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Context variable for downstream access
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

HEADER_NAME = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Ensures every request carries a unique ID (propagated or generated)."""

    def __init__(self, app, header_name: str = HEADER_NAME):
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Reuse incoming ID or generate new one
        incoming = request.headers.get(self.header_name)
        rid = incoming if incoming else str(uuid.uuid4())

        # Set context variable for downstream code
        token = request_id_var.set(rid)

        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)

        # Attach to response headers
        response.headers[self.header_name] = rid
        return response
