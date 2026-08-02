from __future__ import annotations

import json
from typing import Any

from ..api_models import APIResponse


def json_response(
    data: Any,
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> APIResponse:
    """Create a JSON APIResponse."""
    body = json.dumps(data, default=str, ensure_ascii=False)
    response_headers = {"content-type": "application/json"}
    if headers:
        response_headers.update(headers)
    return APIResponse(
        status_code=status,
        body=body,
        headers=response_headers,
        content_type="application/json",
    )


def error_response(
    message: str,
    status: int = 400,
    code: str = "BAD_REQUEST",
    details: dict[str, Any] | None = None,
) -> APIResponse:
    """Create an error APIResponse."""
    payload: dict[str, Any] = {"error": {"message": message, "code": code}}
    if details:
        payload["error"]["details"] = details
    return json_response(payload, status=status)


def html_response(html: str, status: int = 200, headers: dict[str, str] | None = None) -> APIResponse:
    """Create an HTML APIResponse."""
    response_headers = {"content-type": "text/html; charset=utf-8"}
    if headers:
        response_headers.update(headers)
    return APIResponse(
        status_code=status,
        body=html,
        headers=response_headers,
        content_type="text/html",
    )


class ResponseBuilder:
    """Fluent builder for APIResponse objects."""

    def __init__(self) -> None:
        self._status: int = 200
        self._body: Any = None
        self._headers: dict[str, str] = {}
        self._content_type: str = "application/json"

    def json(self, data: Any, status: int = 200) -> dict[str, Any]:
        return {"status": status, "body": json.dumps(data, default=str, ensure_ascii=False)}

    def error(self, status: int, message: str) -> dict[str, Any]:
        return {"status": status, "body": json.dumps({"error": {"message": message}})}

    def empty(self, status: int = 204) -> dict[str, Any]:
        return {"status": status, "body": ""}

    def status(self, code: int) -> ResponseBuilder:
        self._status = code
        return self

    def body(self, data: Any) -> ResponseBuilder:
        self._body = data
        return self

    def header(self, key: str, value: str) -> ResponseBuilder:
        self._headers[key] = value
        return self

    def headers(self, hdrs: dict[str, str]) -> ResponseBuilder:
        self._headers.update(hdrs)
        return self

    def content_type(self, ct: str) -> ResponseBuilder:
        self._content_type = ct
        return self

    def cors(self, origin: str = "*", methods: str = "GET,POST,PUT,PATCH,DELETE,OPTIONS") -> ResponseBuilder:
        self._headers.setdefault("access-control-allow-origin", origin)
        self._headers.setdefault("access-control-allow-methods", methods)
        self._headers.setdefault("access-control-allow-headers", "Authorization,Content-Type,X-Request-ID,X-API-Key")
        self._headers.setdefault("access-control-expose-headers", "X-Request-ID,X-RateLimit-Limit,X-RateLimit-Remaining,X-RateLimit-Reset")
        return self

    def build(self) -> APIResponse:
        body_str = json.dumps(self._body, default=str, ensure_ascii=False) if self._body is not None else ""
        return APIResponse(
            status_code=self._status,
            body=body_str,
            headers=self._headers,
            content_type=self._content_type,
        )

    def to_dict(self) -> dict[str, Any]:
        return {"builder": "ResponseBuilder", "current_status": self._status}
