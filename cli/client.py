from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
from cli.config import CLIConfig


class APIClient:
    def __init__(self, config: CLIConfig | None = None):
        self.config = config or CLIConfig()
        self._client: httpx.AsyncClient | None = None
        self._token: str | None = None

    def _load_token(self) -> str | None:
        token_path = Path.home() / ".superdev" / "token"
        if token_path.exists():
            return token_path.read_text().strip()
        return None

    def _save_token(self, token: str):
        token_path = Path.home() / ".superdev" / "token"
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(token)

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            token = self._token or self._load_token()
            if token:
                headers["Authorization"] = f"Bearer {token}"
            self._client = httpx.AsyncClient(
                base_url=self.config.api_url,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        client = await self._get_client()
        response = await client.request(method, path, **kwargs)
        if response.status_code == 401:
            self._token = None
            raise PermissionError("Authentication required. Run `superdev login`.")
        if response.status_code >= 400:
            detail = response.text
            try:
                body = response.json()
                detail = body.get("detail", body.get("message", response.text))
            except (json.JSONDecodeError, TypeError):
                pass
            raise RuntimeError(f"API error {response.status_code}: {detail}")
        if response.status_code == 204:
            return {}
        return response.json()

    async def get(self, path: str, **kwargs) -> dict[str, Any]:
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs) -> dict[str, Any]:
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs) -> dict[str, Any]:
        return await self.request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs) -> dict[str, Any]:
        return await self.request("DELETE", path, **kwargs)

    async def login(self, email: str, password: str) -> dict[str, Any]:
        result = await self.request("POST", "/api/v1/auth/login", json={"email": email, "password": password})
        token = result.get("access_token") or result.get("token")
        if token:
            self._save_token(token)
            self._token = token
        return result

    async def logout(self):
        token_path = Path.home() / ".superdev" / "token"
        if token_path.exists():
            token_path.unlink()
        self._token = None
        await self.close()

    async def whoami(self) -> dict[str, Any]:
        return await self.get("/api/v1/auth/me")