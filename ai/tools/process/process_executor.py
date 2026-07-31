from __future__ import annotations

import asyncio
from typing import Any

from ...base.base_tool import BaseTool


class ProcessExecutor(BaseTool):
    _name = "process_executor"
    _description = "Execute system processes with full I/O control"
    _permissions = ["write"]

    def __init__(self) -> None:
        self._processes: dict[str, Any] = {}

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
        args = params.get("args", [])
        workdir = params.get("workdir")
        timeout = params.get("timeout", 30)
        full_cmd = [command] + args if isinstance(args, list) else command
        try:
            proc = await asyncio.create_subprocess_exec(
                *full_cmd if isinstance(full_cmd, list) else [full_cmd],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workdir,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace") if stdout else "",
                "stderr": stderr.decode("utf-8", errors="replace") if stderr else "",
                "exit_code": proc.returncode or 0,
                "pid": proc.pid,
            }
        except TimeoutError:
            return {"success": False, "error": f"Process timed out after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        self._processes.clear()
