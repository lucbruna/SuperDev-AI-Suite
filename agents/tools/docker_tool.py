from __future__ import annotations

import asyncio
from typing import Any

from ..base.base_tool import BaseTool


class DockerTool(BaseTool):
    _name = "docker"
    _description = "Build, run, stop, and view logs for Docker containers"
    _permissions = ["execute"]

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        action = params.get("action")
        if action not in ("build", "run", "stop", "logs", "ps", "pull"):
            return False
        return not (action in ("build", "run") and "image" not in params)

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action")
        image = params.get("image", "")
        command = params.get("command", "")
        container_name = params.get("container_name", "")
        dockerfile = params.get("dockerfile", ".")
        timeout = params.get("timeout", 300)

        commands = {
            "ps": ["docker", "ps", "-a"],
            "pull": ["docker", "pull", image],
            "build": ["docker", "build", "-t", image, dockerfile],
            "stop": ["docker", "stop", container_name or image],
            "logs": ["docker", "logs", container_name or image],
        }

        if action == "run":
            cmd_parts = ["docker", "run", "-d"]
            if container_name:
                cmd_parts.extend(["--name", container_name])
            cmd_parts.append(image)
            if command:
                cmd_parts.extend(command.split())
            commands["run"] = cmd_parts

        cmd = commands.get(action)
        if cmd is None:
            return {"success": False, "error": f"Unknown action: {action}"}

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
            return {
                "success": proc.returncode == 0,
                "stdout": stdout.decode("utf-8", errors="replace") if stdout else "",
                "stderr": stderr.decode("utf-8", errors="replace") if stderr else "",
                "exit_code": proc.returncode or 0,
            }
        except TimeoutError:
            return {"success": False, "error": f"Docker operation timed out after {timeout}s"}
        except FileNotFoundError:
            return {"success": False, "error": "Docker not found. Is Docker installed and in PATH?"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
