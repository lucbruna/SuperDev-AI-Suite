import logging
import time
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("superdev")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Any,
    ) -> Response:
        start_time = time.monotonic()
        method = request.method
        path = request.url.path

        response = await call_next(request)

        duration = time.monotonic() - start_time
        status_code = response.status_code

        logger.info(
            "%s %s -> %d (%.3fs)",
            method,
            path,
            status_code,
            duration,
        )
        return response
