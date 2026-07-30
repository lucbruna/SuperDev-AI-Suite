from __future__ import annotations

import asyncio
import json
import time
import urllib.error
import urllib.request
from typing import Any

from ..database_models import ConnectionConfig, QueryResult
from .base_driver import BaseDriver


class Neo4jDriver(BaseDriver):
    """Neo4j driver using HTTP Bolt API via stdlib urllib.

    Communicates with Neo4j through its HTTP API endpoint.
    """

    def __init__(self, logger: Any = None) -> None:
        super().__init__(logger)
        self._base_url: str = ""
        self._auth_header: str = ""

    async def connect(self, config: ConnectionConfig) -> None:
        self._config = config
        scheme = "https" if config.ssl else "http"
        self._base_url = f"{scheme}://{config.host}:{config.port or 7474}"
        if config.username and config.password:
            import base64
            token = base64.b64encode(f"{config.username}:{config.password}".encode()).decode()
            self._auth_header = f"Basic {token}"
        self._connected = True
        self._logger.info(f"Neo4j connected at {self._base_url}")

    async def disconnect(self) -> None:
        self._connected = False

    async def execute(self, query: str, params: list[Any] | None = None) -> QueryResult:
        self._require_connection()
        start = time.monotonic()
        try:
            payload = json.dumps({
                "statements": [{
                    "statement": query,
                    "parameters": dict(zip([f"p{i}" for i in range(len(params or []))], params or [])),
                }],
            }).encode()
            headers = {"Content-Type": "application/json"}
            if self._auth_header:
                headers["Authorization"] = self._auth_header
            req = urllib.request.Request(
                f"{self._base_url}/db/data/transaction/commit",
                data=payload,
                headers=headers,
                method="POST",
            )
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=30))
            data = json.loads(result.read().decode())
            elapsed = (time.monotonic() - start) * 1000
            rows = []
            for res in data.get("results", []):
                for row_data in res.get("data", []):
                    rows.append(row_data)
            return QueryResult(rows=rows, row_count=len(rows), duration_ms=round(elapsed, 2))
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
            elapsed = (time.monotonic() - start) * 1000
            return QueryResult(error=str(exc), duration_ms=round(elapsed, 2))

    @property
    def dialect(self) -> str:
        return "neo4j"

    async def ping(self) -> bool:
        try:
            req = urllib.request.Request(f"{self._base_url}/db/data/")
            if self._auth_header:
                req.add_header("Authorization", self._auth_header)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=5))
            return True
        except Exception:
            return False
