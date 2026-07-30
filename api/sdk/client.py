from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from ..api_logger import APILogger
from .errors import (
    AuthenticationError,
    AuthorizationError,
    ConnectionError,
    NotFoundError,
    RateLimitError,
    SDKError,
    ServerError,
    TimeoutError,
    ValidationError,
)


class BaseClient:
    """Base HTTP client for all SDK protocol clients."""

    def __init__(
        self,
        base_url: str,
        *,
        api_key: str | None = None,
        access_token: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 0,
        logger: APILogger | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._access_token = access_token
        self._timeout = timeout
        self._max_retries = max_retries
        self._logger = logger or APILogger(__name__)
        self._default_headers: dict[str, str] = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._apply_auth()

    def _apply_auth(self) -> None:
        if self._api_key:
            self._default_headers["X-API-Key"] = self._api_key
        if self._access_token:
            self._default_headers["Authorization"] = f"Bearer {self._access_token}"

    def set_token(self, token: str) -> None:
        self._access_token = token
        self._apply_auth()

    def set_api_key(self, api_key: str) -> None:
        self._api_key = api_key
        self._apply_auth()

    def _build_url(self, path: str, params: dict[str, Any] | None = None) -> str:
        url = f"{self.base_url}/{path.lstrip('/')}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        return url

    def _build_request(
        self,
        method: str,
        url: str,
        body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> urllib.request.Request:
        req_headers = {**self._default_headers, **(headers or {})}
        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")
        return urllib.request.Request(url, data=data, headers=req_headers, method=method)

    def _handle_response(self, response: urllib.request.BaseResponse) -> Any:
        body = response.read().decode("utf-8")
        if body:
            return json.loads(body)
        return None

    def _handle_error(self, exc: urllib.error.HTTPError) -> None:
        status = exc.code
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        details = body[:500] if body else None

        error_map: dict[int, type[SDKError]] = {
            400: ValidationError,
            401: AuthenticationError,
            403: AuthorizationError,
            404: NotFoundError,
            429: RateLimitError,
            500: ServerError,
            502: ServerError,
            503: ServerError,
        }
        error_cls = error_map.get(status, SDKError)
        raise error_cls(f"HTTP {status}: {exc.msg}", status_code=status, details=details)

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        url = self._build_url(path, params)
        req = self._build_request(method, url, body, headers)

        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = urllib.request.urlopen(req, timeout=int(self._timeout))
                return self._handle_response(resp)
            except urllib.error.HTTPError as exc:
                if attempt < self._max_retries and exc.code >= 500:
                    time.sleep(2.0 ** attempt)
                    last_exc = exc
                    continue
                self._handle_error(exc)
            except urllib.error.URLError as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    time.sleep(2.0 ** attempt)
                    continue
                raise ConnectionError(f"Connection failed: {exc.reason}") from exc
            except TimeoutError as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    continue
                raise TimeoutError(f"Request timed out after {self._timeout}s") from exc

        raise ConnectionError(f"Request failed after {self._max_retries} retries") from last_exc
