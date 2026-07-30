from __future__ import annotations

import asyncio
import json
import time
import urllib.error
import urllib.request
from typing import Any

from ..database_models import ConnectionConfig, QueryResult
from .base_driver import BaseDriver


class MilvusDriver(BaseDriver):
    """Milvus vector database driver using HTTP API via stdlib urllib."""

    def __init__(self, logger: Any = None) -> None:
        super().__init__(logger)
        self._base_url: str = ""

    async def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        scheme = "https" if config.ssl else "http"
        self._base_url = f"{scheme}://{config.host}:{config.port or 19530}"
        self._connected = True
        self._logger.info(f"Milvus connected at {self._base_url}")

    async def disconnect(self) -> None:
        self._connected = False

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        self._require_connection()
        start = time.monotonic()
        try:
            payload = json.dumps({"query": query, "params": params or []}).encode()
            req = urllib.request.Request(
                f"{self._base_url}/api/v1/query",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30))
            data = json.loads(result.read().decode())
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(
                rows=data.get("data", [data]) if isinstance(data, dict) else [data],
                row_count=1,
                duration_ms=round(elapsed, 2),
            )
        except (urllib.error.HTTPError, urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(error=str(exc), duration_ms=round(elapsed, 2))

    @property
    def dialect(self) -> str:
        return "milvus"

    async def ping(self) -> bool:
        try:
            req = urllib.request.Request(f"{self._base_url}/api/v1/health")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=5))
            return True
        except Exception:
            return False
