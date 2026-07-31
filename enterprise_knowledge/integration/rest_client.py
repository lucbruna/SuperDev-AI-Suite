"""Minimal REST client used by integration bridges and webhooks."""

from __future__ import annotations

import json
from typing import Any
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode


class RestClient:
    """Synchronous REST client with a small surface (timeout + JSON)."""

    def __init__(self, timeout: float = 5.0, headers: dict[str, str] | None = None) -> None:
        self.timeout = timeout
        self.headers = {"Content-Type": "application/json",
                        **(headers or {})}

    def get(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request(url, method="GET", params=params)

    def post(self, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._request(url, method="POST", payload=payload)

    def _request(self, url: str, method: str = "GET",
                 params: dict[str, Any] | None = None,
                 payload: dict[str, Any] | None = None) -> dict[str, Any]:
        target = url
        if params:
            target = f"{url}?{urlencode(params)}"
        request = urllib_request.Request(
            target, method=method, headers=self.headers)
        body: bytes | None = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
        try:
            with urllib_request.urlopen(request, data=body,
                                        timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                return {"ok": True, "status": response.status,
                        "data": json.loads(raw) if raw else None}
        except HTTPError as exc:
            return {"ok": False, "status": exc.code, "error": str(exc)}
        except (URLError, TimeoutError, OSError) as exc:
            return {"ok": False, "status": 0, "error": str(exc)}
