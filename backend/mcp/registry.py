from __future__ import annotations

import json
from typing import Any


class MCPRegistry:
    def __init__(self):
        self._tools: dict[str, dict[str, Any]] = {}
        self._providers: dict[str, str] = {}

    def register_tool(self, name: str, definition: dict[str, Any]) -> None:
        self._tools[name] = {
            **definition,
            "registered_at": __import__("datetime").datetime.utcnow().isoformat(),
        }

    def register_provider(self, provider_id: str, tool_names: list[str]) -> None:
        self._providers[provider_id] = {"tools": tool_names}

    def get_tool(self, name: str) -> dict[str, Any] | None:
        return self._tools.get(name)

    def list_tools(self, provider: str | None = None) -> list[dict[str, Any]]:
        if provider:
            tool_names = self._providers.get(provider, {}).get("tools", [])
            return [self._tools[n] for n in tool_names if n in self._tools]
        return list(self._tools.values())

    def search_tools(self, query: str) -> list[dict[str, Any]]:
        q = query.lower()
        results = []
        for name, tool in self._tools.items():
            if q in name.lower() or q in tool.get("description", "").lower():
                results.append(tool)
        return results

    def get_providers(self) -> list[str]:
        return list(self._providers.keys())

    def unregister_tool(self, name: str) -> bool:
        return self._tools.pop(name, None) is not None

    def to_dict(self) -> dict[str, Any]:
        return {"tools": self._tools, "providers": self._providers}

    def load_from_file(self, path: str) -> None:
        with open(path) as f:
            data = json.load(f)
        for tool in data.get("tools", []):
            self.register_tool(tool["name"], tool)
        for provider in data.get("providers", []):
            self.register_provider(provider["id"], provider.get("tool_names", []))

    def count(self) -> int:
        return len(self._tools)
