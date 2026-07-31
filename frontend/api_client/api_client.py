from __future__ import annotations

import logging
from typing import Any, Callable

import urllib.error
import urllib.parse
import urllib.request


class APIClient:
    """HTTP client for the backend API."""

    def __init__(self, base_url: str = "/api", headers: dict[str, str] | None = None) -> None:
        self._log = logging.getLogger("superdev.frontend.api")
        self.base_url = base_url.rstrip("/")
        self._headers = dict(headers or {})
        self._interceptors: list[Callable[[str, str, dict[str, Any]], dict[str, Any]]] = []

    def get(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, data: Any = None, **kwargs: Any) -> dict[str, Any]:
        return self.request("POST", path, data=data, **kwargs)

    def put(self, path: str, data: Any = None, **kwargs: Any) -> dict[str, Any]:
        return self.request("PUT", path, data=data, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> dict[str, Any]:
        return self.request("DELETE", path, **kwargs)

    def request(self, method: str, path: str, data: Any = None, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        payload = data
        for interceptor in self._interceptors:
            payload = interceptor(method, url, payload)
        return self._dispatch(method, url, payload, **kwargs)

    def _dispatch(self, method: str, url: str, data: Any, **kwargs: Any) -> dict[str, Any]:
        headers = dict(self._headers)
        body = None
        if data is not None:
            body = data.encode() if isinstance(data, str) else urllib.parse.urlencode(data).encode()
            headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=float(kwargs.get("timeout", 10))) as response:
                status = response.status
                raw = response.read()
        except urllib.error.HTTPError as error:
            status = error.code
            raw = error.read()
        except urllib.error.URLError as error:
            return {"status": 0, "ok": False, "error": str(error.reason)}
        try:
            import json

            content = json.loads(raw.decode("utf-8"))
        except Exception:
            content = raw.decode("utf-8", errors="replace")
        return {"status": status, "ok": 200 <= status < 300, "data": content}

    def add_interceptor(self, interceptor: Callable[[str, str, Any], Any]) -> None:
        self._interceptors.append(interceptor)

    def set_header(self, key: str, value: str) -> None:
        self._headers[key] = value

    def clear_headers(self) -> None:
        self._headers.clear()

    def url(self, path: str) -> str:
        return f"{self.base_url}{path}"
