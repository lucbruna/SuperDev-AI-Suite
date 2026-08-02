from __future__ import annotations

import uuid
from typing import Any

from ..api_interfaces import IAPIMiddleware


class RequestIDMiddleware(IAPIMiddleware):
    """Ensures every request has a unique request ID."""

    def __init__(self, header_name: str = "X-Request-ID") -> None:
        self._header_name = header_name

    def generate_id(self) -> str:
        return str(uuid.uuid4())

    async def before_request(self, request: Any) -> Any:
        headers = getattr(request, "headers", {}) if hasattr(request, "headers") else {}
        request_id = ""
        if isinstance(headers, dict):
            request_id = headers.get(self._header_name.lower(), headers.get(self._header_name, ""))
        if not request_id:
            request_id = str(uuid.uuid4())
        if hasattr(request, "request_id"):
            request.request_id = request_id
        return None

    async def after_request(self, response: Any) -> Any:
        if hasattr(response, "headers") and isinstance(response.headers, dict):
            response.headers[self._header_name] = getattr(response, "request_id", "")
        return response

    def to_dict(self) -> dict[str, Any]:
        return {"middleware": "RequestIDMiddleware", "header": self._header_name}
