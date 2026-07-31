from __future__ import annotations

from abc import ABC, abstractmethod

import httpx


class BaseGateway(ABC):
    """Base gateway for external API integrations."""

    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=self._build_headers(),
            timeout=30.0,
        )

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    @abstractmethod
    async def health_check(self) -> bool: ...

    async def close(self) -> None:
        await self._client.aclose()
