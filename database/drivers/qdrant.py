from __future__ import annotations

import asyncio
import json
import time
import urllib.error
import urllib.request
from typing import Any

from ..database_models import ConnectionConfig, QueryResult
from .base_driver import BaseDriver


class QdrantDriver(BaseDriver):
    """Qdrant vector database driver using REST API via stdlib urllib."""

    def __init__(self, logger: Any = None) -> None:
        super().__init__(logger)
        self._base_url: str = ""
        self._headers: dict[str, str] = {}

    async def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        scheme = "https" if config.ssl else "http"
        self._base_url = f"{scheme}://{config.host}:{config.port or 6333}"
        self._headers = {"Content-Type": "application/json"}
        if config.api_key:
            self._headers["api-key"] = config.api_key
        self._connected = True
        self._logger.info(f"Qdrant connected at {self._base_url}")

    async def disconnect(self) -> None:
        self._connected = False

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        self._require_connection()
        start = time.monotonic()
        try:
            url = f"{self._base_url}/{query.lstrip('/')}"
            body = json.dumps(params[0] if params else {}).encode() if params else None
            method = "POST" if body else "GET"
            req = urllib.request.Request(url, data=body, headers=self._headers, method=method)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30))
            data = json.loads(result.read().decode())
            elapsed = (time.monotonic() - start) * 1000
            rows = data.get("result", data) if isinstance(data, dict) else data
            return QueryResult(
                rows=[rows] if isinstance(rows, dict) else rows if isinstance(rows, list) else [],
                row_count=1 if isinstance(rows, dict) else len(rows) if isinstance(rows, list) else 0,
                duration_ms=round(elapsed, 2),
            )
        except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(error=str(exc), duration_ms=round(elapsed, 2))

    @property
    def dialect(self) -> str:
        return "qdrant"

    async def ping(self) -> bool:
        try:
            req = urllib.request.Request(f"{self._base_url}/health")
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=5))
            return result.getcode() == 200
        except Exception:
            return False
