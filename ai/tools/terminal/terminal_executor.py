from __future__ import annotations

import asyncio
import os
from typing import Any

from ...base.base_tool import BaseTool


class TerminalExecutor(BaseTool):
    _name = "terminal_executor"
    _description = "Execute shell commands with timeout and environment control"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "command" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        command = params["command"]
        workdir = params.get("workdir")
        timeout = params.get("timeout", 60)
        env = params.get("env", {})
        try:
            exec_env = os.environ.copy()
            exec_env.update(env)
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workdir,
                env=exec_env,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            result = {
                "success": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace") if stdout else "",
                "stderr": stderr.decode("utf-8", errors="replace") if stderr else "",
                "exit_code": proc.returncode or 0,
            }
            self._history.append({"command": command, "result": result})
            return result
        except TimeoutError:
            return {"success": False, "stdout": "", "stderr": f"Timed out after {timeout}s", "exit_code": -1}
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}

    async def rollback(self) -> None:
        self._history.clear()

    async def cleanup(self) -> None:
        self._history.clear()
