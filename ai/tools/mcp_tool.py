from __future__ import annotations

from typing import Any

from backend.mcp.server import register_tool, register_handler, ToolDefinition
from backend.mcp.client import MCPClient


class MCPTool:
    def __init__(self, mcp_client: MCPClient | None = None):
        self._client = mcp_client or MCPClient()
        self._tool_cache: dict[str, Any] | None = None

    async def discover_tools(self) -> list[dict[str, Any]]:
        tools = await self._client.list_tools()
        self._tool_cache = {t["name"]: t for t in tools}
        return tools

    async def execute(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return await self._client.call_tool(tool_name, arguments)

    async def execute_with_agent(self, agent_id: str, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        result = await self.execute(tool_name, arguments)
        return {"agent_id": agent_id, "tool": tool_name, "result": result}

    async def batch_execute(self, calls: list[dict[str, Any]]) -> list[dict[str, Any]]:
        import asyncio
        async def single(call: dict[str, Any]) -> dict[str, Any]:
            return await self.execute(call["tool_name"], call.get("arguments", {}))
        return await asyncio.gather(*[single(c) for c in calls])

    def find_tool(self, query: str) -> list[dict[str, Any]]:
        if not self._tool_cache:
            return []
        q = query.lower()
        return [t for t in self._tool_cache.values() if q in t["name"].lower() or q in t.get("description", "").lower()]

    async def auto_select_tool(self, task_description: str) -> dict[str, Any] | None:
        tools = await self.discover_tools()
        q = task_description.lower()
        candidates = []
        for t in tools:
            desc = t.get("description", "").lower()
            name = t["name"].lower()
            score = 0
            for word in q.split():
                if word in desc:
                    score += 2
                if word in name:
                    score += 3
            if score > 0:
                candidates.append((score, t))
        candidates.sort(key=lambda x: -x[0])
        return candidates[0][1] if candidates else None


def register_mcp_handler(name: str, description: str, input_schema: dict[str, Any], handler: callable) -> None:
    tool_def = ToolDefinition(name=name, description=description, input_schema=input_schema)
    register_tool(tool_def)
    register_handler(name, handler)