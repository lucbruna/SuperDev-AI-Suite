from __future__ import annotations

import time
import uuid
from typing import Any

from .tool_interfaces import IToolExecutor
from .tool_logger import ToolLogger
from .tool_metrics import ToolMetrics
from .tool_registry import ToolRegistry
from .tool_validator import ToolValidator


class ToolExecutor(IToolExecutor):
    """Executes tools with validation, metrics, and logging."""

    def __init__(
        self, registry: ToolRegistry, validator: ToolValidator, metrics: ToolMetrics, logger: ToolLogger
    ) -> None:
        self._registry = registry
        self._validator = validator
        self._metrics = metrics
        self._logger = logger

    async def validate(self, tool_name: str, params: dict[str, Any]) -> bool:
        return await self._validator.validate(tool_name, params)

    async def execute(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        tool = self._registry.get(tool_name)
        if tool is None:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        valid = await tool.validate(params)
        if not valid:
            self._metrics.record_error(tool_name)
            return {"success": False, "error": "Parameter validation failed"}

        execution_id = str(uuid.uuid4())
        start = time.time()

        try:
            self._logger.info(tool_name, f"Starting execution {execution_id}", params=params)
            result = await tool.execute(params)
            duration = time.time() - start
            self._metrics.record_execution(tool_name, duration)
            result["execution_id"] = execution_id
            result["duration_ms"] = round(duration * 1000, 2)
            self._logger.info(
                tool_name,
                f"Completed execution {execution_id}",
                duration_ms=result["duration_ms"],
                success=result.get("success"),
            )
            return result
        except Exception as e:
            duration = time.time() - start
            self._metrics.record_error(tool_name)
            self._logger.error(tool_name, f"Execution failed: {e}", execution_id=execution_id)
            return {
                "success": False,
                "error": str(e),
                "execution_id": execution_id,
                "duration_ms": round(duration * 1000, 2),
            }

    async def execute_batch(self, tasks: list[tuple[str, dict[str, Any]]]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for tool_name, params in tasks:
            result = await self.execute(tool_name, params)
            results.append(result)
        return results

    async def rollback(self, tool_name: str) -> None:
        tool = self._registry.get(tool_name)
        if tool:
            await tool.rollback()

    async def cleanup(self, tool_name: str) -> None:
        tool = self._registry.get(tool_name)
        if tool:
            await tool.cleanup()

    def to_dict(self) -> dict[str, Any]:
        return {
            "registered_tools": self._registry.list_names(),
            "metrics": self._metrics.to_dict(),
        }
