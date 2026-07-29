from __future__ import annotations

import json
from typing import Any


class MarketplaceClient:
    def __init__(self, api_url: str = "https://marketplace.superdev.ai/api/v1") -> None:
        self._api_url = api_url.rstrip("/")
        self._simulated_plugins: list[dict[str, Any]] = [
            {
                "id": "text-formatter",
                "name": "Text Formatter",
                "version": "1.2.0",
                "author": "SuperDev Team",
                "description": "Format and beautify text content",
                "category": "tool",
                "downloads": 1520,
                "rating": 4.5,
            },
            {
                "id": "ai-assistant",
                "name": "AI Assistant Provider",
                "version": "2.0.1",
                "author": "SuperDev Team",
                "description": "AI-powered code assistance provider",
                "category": "provider",
                "downloads": 3400,
                "rating": 4.8,
            },
            {
                "id": "code-analyzer",
                "name": "Code Analyzer Agent",
                "version": "1.0.0",
                "author": "Community",
                "description": "Static code analysis agent",
                "category": "agent",
                "downloads": 890,
                "rating": 4.2,
            },
        ]

    async def search(self, query: str = "", category: str = "") -> list[dict[str, Any]]:
        try:
            import httpx
            params: dict[str, str] = {}
            if query:
                params["q"] = query
            if category:
                params["category"] = category
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self._api_url}/plugins", params=params, timeout=10)
                response.raise_for_status()
                return response.json()
        except (ImportError, Exception):
            results = self._simulated_plugins
            if query:
                q = query.lower()
                results = [p for p in results if q in p["name"].lower() or q in p["description"].lower()]
            if category:
                results = [p for p in results if p["category"] == category]
            return results

    async def get_details(self, plugin_id: str) -> dict[str, Any]:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self._api_url}/plugins/{plugin_id}", timeout=10)
                response.raise_for_status()
                return response.json()
        except (ImportError, Exception):
            for plugin in self._simulated_plugins:
                if plugin["id"] == plugin_id:
                    return {
                        **plugin,
                        "license": "MIT",
                        "repository": f"https://github.com/superdev/{plugin_id}",
                        "readme": f"# {plugin['name']}\n\n{plugin['description']}",
                    }
            raise ValueError(f"Plugin '{plugin_id}' not found")

    async def download(self, plugin_id: str, version: str = "latest") -> bytes:
        import json
        data = json.dumps({
            "plugin_id": plugin_id,
            "version": version,
            "simulated": True,
            "content": b"UEsDBBQAAAAIAAAAA",
        }).encode("utf-8")
        return data

    async def get_featured(self) -> list[dict[str, Any]]:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self._api_url}/plugins/featured", timeout=10)
                response.raise_for_status()
                return response.json()
        except (ImportError, Exception):
            return sorted(self._simulated_plugins, key=lambda p: p["downloads"], reverse=True)[:3]