from __future__ import annotations

import json
import time
import urllib.parse
from typing import Any

from ..api_models import APIRequest


def parse_query_string(query_string: str) -> dict[str, list[str]]:
    """Parse a URL query string into a dict of key -> [values]."""
    if not query_string:
        return {}
    parsed = urllib.parse.parse_qs(query_string, keep_blank_values=True)
    return {k: v for k, v in parsed.items()}


def parse_headers(headers_list: list[tuple[bytes, bytes]]) -> dict[str, str]:
    """Parse raw ASGI headers list into a dict."""
    return {k.decode(): v.decode() for k, v in headers_list}


def parse_request_body(body_bytes: bytes, content_type: str) -> Any:
    """Parse a raw request body based on content type."""
    if not body_bytes:
        return None
    content_type_lower = content_type.lower()
    if "json" in content_type_lower:
        return json.loads(body_bytes)
    if "x-www-form-urlencoded" in content_type_lower:
        parsed = urllib.parse.parse_qs(body_bytes.decode("utf-8", errors="replace"))
        return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
    return body_bytes.decode("utf-8", errors="replace")


class RequestParser:
    """Parses raw ASGI scope + receive into an APIRequest."""

    def parse_json(self, body: bytes | str | Any) -> Any:
        if isinstance(body, (bytes, bytearray)):
            return json.loads(body)
        if isinstance(body, str):
            return json.loads(body)
        return body

    def parse_query(self, query_string: str) -> dict[str, str]:
        parsed = urllib.parse.parse_qs(query_string, keep_blank_values=True)
        return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

    def parse(self, scope: dict[str, Any], body_bytes: bytes = b"") -> APIRequest:
        method = scope.get("method", "GET")
        path = scope.get("path", "/")
        raw_headers = scope.get("headers", [])
        headers = parse_headers(raw_headers)
        query_string = scope.get("query_string", b"").decode("utf-8", errors="replace")
        query = parse_query_string(query_string)
        content_type = headers.get("content-type", "application/json")
        body = parse_request_body(body_bytes, content_type)
        client_ip = headers.get("x-forwarded-for", "").split(",")[0].strip() or scope.get("client", ("", 0))[0] or ""
        request_id = headers.get("x-request-id", "")
        return APIRequest(
            method=method,
            path=path,
            headers=headers,
            query=query,
            body=body,
            content_type=content_type,
            client_ip=client_ip,
            request_id=request_id,
            timestamp=time.time(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"parser": "ASGIRequestParser"}
