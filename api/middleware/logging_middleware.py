from __future__ import annotations

import time
from typing import Any

from ..api_interfaces import IAPIMiddleware
from ..api_logger import APILogger


class LoggingMiddleware(IAPIMiddleware):
    """Logs request/response information."""

    def __init__(self, logger: APILogger | None = None) -> None:
        self._logger = logger or APILogger("api.middleware")

    async def before_request(self, request: Any) -> Any:
        self._start_time = time.time()
        self._logger.info(
            "Request started",
            method=getattr(request, "method", ""),
            path=getattr(request, "path", ""),
            request_id=getattr(request, "request_id", ""),
        )
        return None

    async def after_request(self, response: Any) -> Any:
        elapsed = (time.time() - self._start_time) * 1000
        self._logger.info(
            "Request completed",
            status=getattr(response, "status_code", 0),
            elapsed_ms=round(elapsed, 2),
            request_id=getattr(response, "request_id", ""),
        )
        return response

    def to_dict(self) -> dict[str, Any]:
        return {"middleware": "LoggingMiddleware"}
