from __future__ import annotations

import json
import time
from typing import Any
from urllib import request as url_request
from urllib.error import HTTPError, URLError

from security.ssrf import validate_public_url

from ..data_models import DataSourceType
from .collector import BaseCollector
from .connector import BaseConnector


class APIConnector(BaseConnector):
    """REST API connector using the Python standard library (urllib).

    Config keys:
        url: base endpoint
        method: HTTP method (default "GET")
        headers: dict of default headers
        timeout: request timeout in seconds (default 10)
        pagination: optional dict with {"param", "per_page", "total_param"}
        max_pages: safety cap on paginated requests (default 100)
    """

    def __init__(self, name: str, config: dict[str, Any] | None = None) -> None:
        super().__init__(name, config)
        self._base_url = self.config.get("url", "")

    async def connect(self) -> bool:
        self.connected = bool(self._base_url)
        return self.connected

    async def read(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        query = query or {}
        url = query.get("url") or self._base_url
        if not url:
            raise ValueError(f"API connector '{self.name}' has no url configured")

        method = query.get("method") or self.config.get("method", "GET")
        headers = {**self.config.get("headers", {}), **query.get("headers", {})}
        timeout = float(query.get("timeout") or self.config.get("timeout", 10.0))

        body = None
        if "json" in query:
            body = json.dumps(query["json"]).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")

        # SSRF guard (CWE-918): validate once before any request — the host
        # never changes across pagination pages. Refuse private/loopback/
        # metadata targets unless the connector opts in via ``allow_private_urls``.
        url = validate_public_url(
            url,
            allow_private=bool(self.config.get("allow_private_urls", False)),
        )

        rows: list[dict[str, Any]] = []
        page = query.get("page") or 1
        pagination = query.get("pagination") or self.config.get("pagination")
        max_pages = int(query.get("max_pages") or self.config.get("max_pages", 100))
        fetched_pages = 0
        while True:
            fetched_pages += 1
            if fetched_pages > max_pages:
                raise ValueError(
                    f"API connector '{self.name}' exceeded max_pages={max_pages} "
                    "(server may be ignoring the page parameter)"
                )
            page_url = url
            if pagination:
                sep = "&" if "?" in page_url else "?"
                page_url = f"{page_url}{sep}{pagination.get('param', 'page')}={page}"
            payload = self._request(page_url, method, headers, timeout, body)
            page_rows, next_page = self._parse_payload(payload, pagination, page)
            rows.extend(page_rows)
            if next_page is None or not pagination:
                break
            page = next_page

        self._last_read_at = time.time()
        return rows

    def _parse_payload(
        self,
        payload: Any,
        pagination: dict[str, Any] | None,
        page: int,
    ) -> tuple[list[dict[str, Any]], int | None]:
        if isinstance(payload, list):
            rows = [dict(item) for item in payload if isinstance(item, dict)]
            return self._pagination_decision(rows, pagination, page)
        if isinstance(payload, dict):
            items = payload.get("results") or payload.get("data") or payload.get("items") or []
            rows = [dict(item) for item in items if isinstance(item, dict)]
            return self._pagination_decision(rows, pagination, page)
        return [], None

    @staticmethod
    def _pagination_decision(
        rows: list[dict[str, Any]],
        pagination: dict[str, Any] | None,
        page: int,
    ) -> tuple[list[dict[str, Any]], int | None]:
        """Heuristic: if a page is full (>= per_page rows), ask for the next one."""
        if pagination:
            per_page = int(pagination.get("per_page", 20))
            if len(rows) >= per_page:
                return rows, page + 1
        return rows, None

    def _request(
        self,
        url: str,
        method: str,
        headers: dict[str, str],
        timeout: float,
        body: bytes | None,
    ) -> Any:
        request = url_request.Request(url, data=body, headers=headers, method=method)
        try:
            with url_request.urlopen(request, timeout=timeout) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            raise ValueError(f"API connector '{self.name}' HTTP {exc.code}: {exc.reason}") from exc
        except URLError as exc:
            raise ValueError(f"API connector '{self.name}' connection error: {exc.reason}") from exc
        return json.loads(raw)

    async def disconnect(self) -> None:
        self.connected = False


class APICollector(BaseCollector):
    """Collector that pulls records from a REST API via :class:`APIConnector`."""

    def __init__(
        self,
        name: str,
        connector: APIConnector | None = None,
        engine: Any | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, engine, config)
        self.connector = connector or APIConnector(name, config or {})

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.API

    async def collect(self, config: dict[str, Any] | None = None) -> Any:
        merged = {**self.config, **(config or {})}
        await self.connector.connect()
        try:
            rows = await self.connector.read(merged)
        finally:
            await self.connector.disconnect()
        return self._build_batch(rows, metadata={"connector": "api"})


__all__ = ["APIConnector", "APICollector"]
