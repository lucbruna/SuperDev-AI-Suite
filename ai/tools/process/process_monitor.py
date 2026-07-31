from __future__ import annotations

import os
import signal
from typing import Any

from ...base.base_tool import BaseTool


class ProcessMonitor(BaseTool):
    _name = "process_monitor"
    _description = "List, monitor, and kill system processes"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._killed: list[int] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "list")
        try:
            if action == "list":
                processes: list[dict[str, Any]] = []
                for pid in os.listdir("/proc") if os.name != "nt" else []:
                    if pid.isdigit():
                        try:
                            with open(f"/proc/{pid}/comm") as f:
                                name = f.read().strip()
                            processes.append({"pid": int(pid), "name": name})
                        except OSError:
                            pass
                if os.name == "nt":
                    import subprocess

                    result = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True)
                    for line in result.stdout.strip().split("\n"):
                        if line:
                            parts = line.strip('"').split('","')
                            if len(parts) >= 2:
                                processes.append({"name": parts[0], "pid": parts[1]})
                return {"success": True, "processes": processes[:50], "count": min(len(processes), 50)}
            elif action == "status":
                pid = params.get("pid", 0)
                try:
                    os.kill(pid, 0)
                    return {"success": True, "pid": pid, "running": True}
                except (OSError, ProcessLookupError):
                    return {"success": True, "pid": pid, "running": False}
            elif action == "kill":
                pid = params.get("pid", 0)
                sig = params.get("signal", signal.SIGTERM)
                try:
                    os.kill(pid, sig)
                    self._killed.append(pid)
                    return {"success": True, "pid": pid, "signal": sig}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._killed.clear()

    async def cleanup(self) -> None:
        self._killed.clear()
