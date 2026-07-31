"""HTTP API datasource ingestion."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from data_intelligence.data_models import SourceType
from data_intelligence.ingestion.base import BaseSource
from security.ssrf import validate_public_url


class ApiSource(BaseSource):
    """Fetches records from a REST API.

    Uses ``urllib.request`` for the default implementation; pass a custom
    ``requester`` callable (e.g. ``requests.get``) when authentication or
    headers are required.
    """

    source_type = SourceType.API

    def __init__(self, source_id: str, name: str, endpoint: str,
                 headers: dict[str, str] | None = None,
                 requester: Any = None, **config: Any) -> None:
        super().__init__(source_id, name, endpoint=endpoint,
                         headers=headers, requester=requester, **config)
        self.endpoint = endpoint
        self.headers = headers or {}
        self._requester = requester

    def fetch(self, source: Any = None) -> Iterable[dict[str, Any]]:  # noqa: ARG002
        if self._requester is not None:
            return self._fetch_custom()
        payload = self._default_request()
        if isinstance(payload, list):
            return payload
        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]
        if isinstance(payload, dict) and "results" in payload:
            return payload["results"]
        return [payload] if isinstance(payload, dict) else []

    def _default_request(self) -> Any:
        import json
        import urllib.request

        # SSRF guard (CWE-918): refuse private/loopback/metadata targets unless
        # the source explicitly opts in via ``allow_private``.
        validate_public_url(
            self.endpoint,
            allow_private=bool(self.config.get("allow_private", False)),
        )
        request = urllib.request.Request(self.endpoint, headers=self.headers)
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))

    def _fetch_custom(self) -> list[dict[str, Any]]:
        response = self._requester(self.endpoint, headers=self.headers)
        data = response
        if hasattr(response, "json"):
            data = response.json()
        if isinstance(data, dict):
            for key in ("data", "results", "items"):
                if key in data:
                    return list(data[key])
        return [dict(item) for item in data] if isinstance(data, list) else []
