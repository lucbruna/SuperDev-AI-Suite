from __future__ import annotations

import asyncio
import os
from typing import Any


class TerminalTool:
    _name = "terminal"
    _description = "Execute shell commands and return output"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._operations_log: list[dict[str, Any]] = []
        self._processes: dict[str, asyncio.subprocess.Process] = {}

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "command" in params and isinstance(params["command"], str)

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        command = params.get("command", "")
        workdir = params.get("workdir")
        timeout = params.get("timeout", 60)
        env = params.get("env", {})

        if not command:
            return {"success": False, "stdout": "", "stderr": "No command provided", "exit_code": -1}

        # Save working directory for potential rollback (cd operations)
        original_dir = os.getcwd() if workdir else None

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
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout
            )

            result = {
                "success": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace") if stdout else "",
                "stderr": stderr.decode("utf-8", errors="replace") if stderr else "",
                "exit_code": proc.returncode or 0,
            }

            self._log_operation(command, workdir, result=result)
            return result

        except asyncio.TimeoutError:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "exit_code": -1,
            }
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "exit_code": -1}

    async def rollback(self) -> None:
        """Rollback is limited for terminal commands - logs the attempt."""
        if not self._operations_log:
            return
        last = self._operations_log.pop()
        command = last.get("command", "")
        # Terminal commands are hard to roll back automatically
        # Log for awareness
        self._operations_log.append({
            "operation": "rollback_attempt",
            "original_command": command,
            "note": "Terminal commands cannot be automatically rolled back",
        })

    async def cleanup(self) -> None:
        self._operations_log.clear()

    def _log_operation(self, command: str, workdir: str | None, **kwargs: Any) -> None:
        self._operations_log.append({
            "operation": "execute",
            "command": command,
            "workdir": workdir,
            **kwargs,
        })
