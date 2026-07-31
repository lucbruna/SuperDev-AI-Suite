from __future__ import annotations

import asyncio
import base64
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from ..database_models import ConnectionConfig, QueryResult
from .base_driver import BaseDriver


class ClickHouseDriver(BaseDriver):
    """ClickHouse driver using HTTP interface via stdlib urllib."""

    def __init__(self, logger: Any = None) -> None:
        super().__init__(logger)
        self._base_url: str = ""
        self._auth: str = ""  # HTTP Basic credentials (base64 user:password)

    async def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        scheme = "https" if config.ssl else "http"
        port = config.port or 8123
        self._base_url = f"{scheme}://{config.host}:{port}"
        if config.username:
            # Credentials via HTTP Basic auth header — never in the URL query
            # string (would leak into logs/proxies).
            userpass = f"{config.username}:{config.password or ''}".encode()
            self._auth = base64.b64encode(userpass).decode("ascii")
        self._connected = True
        self._logger.info(f"ClickHouse connected at {self._base_url}")

    async def disconnect(self) -> None:
        self._connected = False

    async def execute(self, query: str, _params: list[Any] | None = None) -> QueryResult:
        self._require_connection()
        start = time.monotonic()
        try:
            url = f"{self._base_url}/?query={urllib.parse.quote(query)}"
            headers = {"Authorization": f"Basic {self._auth}"} if self._auth else {}
            req = urllib.request.Request(url, headers=headers)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30))
            body = result.read().decode()
            elapsed = (time.monotonic() - start) * 1000
            rows = []
            if body.strip():
                lines = body.strip().split("\n")
                for line in lines:
                    if line.strip():
                        rows.append({"result": line.strip()})
            return QueryResult(rows=rows, row_count=len(rows), duration_ms=round(elapsed, 2))
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(error=str(exc), duration_ms=round(elapsed, 2))

    @property
    def dialect(self) -> str:
        return "clickhouse"

    async def ping(self) -> bool:
        try:
            req = urllib.request.Request(f"{self._base_url}/ping")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=5))
            return result.getcode() == 200
        except Exception:
            return False
