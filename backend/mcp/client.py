from __future__ import annotations

from typing import Any

import httpx


class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8000/mcp"):
        self._base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=30.0)
        self._session_id: str | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._client.aclose()

    async def list_tools(self) -> list[dict[str, Any]]:
        resp = await self._client.get(f"{self._base_url}/tools")
        resp.raise_for_status()
        return resp.json()

    async def get_tool(self, name: str) -> dict[str, Any]:
        resp = await self._client.get(f"{self._base_url}/tools/{name}")
        resp.raise_for_status()
        return resp.json()

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        payload = {"tool_name": tool_name, "arguments": arguments, "session_id": self._session_id}
        resp = await self._client.post(f"{self._base_url}/call", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def create_session(self, context: dict[str, Any] | None = None) -> dict[str, Any]:
        resp = await self._client.post(f"{self._base_url}/session", json={"context": context or {}})
        resp.raise_for_status()
        data = resp.json()
        self._session_id = data["session_id"]
        return data

    async def get_session(self, session_id: str | None = None) -> dict[str, Any]:
        sid = session_id or self._session_id
        if not sid:
            raise ValueError("No session ID set")
        resp = await self._client.get(f"{self._base_url}/session/{sid}")
        resp.raise_for_status()
        return resp.json()

    def set_session(self, session_id: str) -> None:
        self._session_id = session_id
