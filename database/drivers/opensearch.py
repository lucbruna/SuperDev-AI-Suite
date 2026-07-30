from __future__ import annotations

import asyncio
import json
import time
import urllib.error
import urllib.request
from typing import Any

from ..database_models import ConnectionConfig, QueryResult
from .base_driver import BaseDriver


class OpenSearchDriver(BaseDriver):
    """OpenSearch driver using HTTP REST API via stdlib urllib."""

    def __init__(self, logger: Any = None) -> None:
        super().__init__(logger)
        self._base_url: str = ""
        self._headers: dict[str, str] = {}

    async def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        scheme = "https" if config.ssl else "http"
        self._base_url = f"{scheme}://{config.host}:{config.port or 9200}"
        self._headers = {"Content-Type": "application/json"}
        if config.username and config.password:
            import base64
            token = base64.b64encode(f"{config.username}:{config.password}".encode()).decode()
            self._headers["Authorization"] = f"Basic {token}"
        self._connected = True
        self._logger.info(f"OpenSearch connected at {self._base_url}")

    async def disconnect(self) -> None:
        self._connected = False

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        self._require_connection()
        start = time.monotonic()
        try:
            body = query.encode() if isinstance(query, str) else query
            url = f"{self._base_url}/{params[0] if params else '_search'}"
            req = urllib.request.Request(url, data=body, headers=self._headers, method="POST")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30))
            data = json.loads(result.read().decode())
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(
                rows=[data] if isinstance(data, dict) else data,
                row_count=1,
                duration_ms=round(elapsed, 2),
            )
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(error=str(exc), duration_ms=round(elapsed, 2))

    @property
    def dialect(self) -> str:
        return "opensearch"

    async def ping(self) -> bool:
        try:
            req = urllib.request.Request(f"{self._base_url}/")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=5))
            return True
        except Exception:
            return False
