from __future__ import annotations

from typing import Any

from ..base.base_agent import AgentResult, BaseAgent
from ..tools.filesystem_tool import FilesystemTool
from ..tools.terminal_tool import TerminalTool
from ..tools.python_tool import PythonTool
from ..tools.git_tool import GitTool


class ExecutorAgent(BaseAgent):
    async def initialize(self) -> None:
        self._filesystem = FilesystemTool()
        self._terminal = TerminalTool()
        self._python = PythonTool()
        self._git = GitTool()
        self._status = "ready"

    async def execute(self, task: str, context: dict[str, Any]) -> AgentResult:
        try:
            await self._check_cancelled()
            self._status = "running"
            tool_name = context.get("tool", "terminal")
            params = context.get("params", {})
            params["command"] = params.get("command", task)

            if tool_name == "filesystem":
                result = await self._filesystem.execute(params)
            elif tool_name == "python":
                result = await self._python.execute(params)
            elif tool_name == "git":
                result = await self._git.execute(params)
            else:
                result = await self._terminal.execute(params)

            return AgentResult(
                success=result.get("success", False),
                output=result.get("stdout", "") or result.get("content", "") or str(result),
                error=result.get("stderr", "") or result.get("error", ""),
                metrics={"tool_used": tool_name},
                artifacts={"result": result},
            )
        except Exception as e:
            self._error_count += 1
            return AgentResult(success=False, output="", error=str(e))
        finally:
            self._status = "idle"

    def capabilities(self) -> list[str]:
        return ["file_operations", "command_execution", "python_execution", "git_operations"]
