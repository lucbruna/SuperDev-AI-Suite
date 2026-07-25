from __future__ import annotations

import asyncio
from typing import Any, Optional

from ..base.base_agent import BaseAgent
from ..base.base_tool import BaseTool
from ..core.agent_system import AgentSystem
from ..registry.tool_registry import ToolRegistry


class TaskRunner:
    def __init__(
        self,
        agent_system: Optional[AgentSystem] = None,
        tool_registry: Optional[ToolRegistry] = None,
    ) -> None:
        self._agent_system = agent_system or AgentSystem()
        self._tool_registry = tool_registry or ToolRegistry()

    async def run_task(self, task: str, context: dict[str, Any]) -> dict[str, Any]:
        agent_name = context.get("assigned_agent", "")
        if agent_name:
            result = await self._run_with_agent(agent_name, task, context)
            return result

        tool_name = context.get("assigned_tool", "")
        if tool_name:
            result = await self._run_with_tool(tool_name, context.get("params", {}))
            return result

        return {"success": False, "error": "No agent or tool assigned in context"}

    async def _run_with_agent(self, agent_name: str, task: str, context: dict[str, Any]) -> dict[str, Any]:
        agent_result = await self._agent_system.execute_task(agent_name, task, context)
        return {
            "success": agent_result.success,
            "output": agent_result.output,
            "error": agent_result.error,
            "metrics": agent_result.metrics,
            "artifacts": agent_result.artifacts,
        }

    async def _run_with_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        tool_class = self._tool_registry.get(tool_name)
        if tool_class is None:
            return {"success": False, "error": f"Tool '{tool_name}' not found"}
        tool_instance = tool_class()
        valid = await tool_instance.validate(params)
        if not valid:
            return {"success": False, "error": "Parameter validation failed"}
        try:
            result = await tool_instance.execute(params)
            return {"success": True, "output": result, "error": ""}
        except Exception as e:
            return {"success": False, "error": str(e)}
