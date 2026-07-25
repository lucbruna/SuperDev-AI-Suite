from __future__ import annotations

import asyncio
from typing import Any

from ..base.base_tool import BaseTool


class GitTool(BaseTool):
    _name = "git"
    _description = "Execute Git commands: clone, commit, push, pull, status"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._operations_log: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        action = params.get("action")
        if action not in ("clone", "commit", "push", "pull", "status", "log", "checkout", "revert"):
            return False
        if action == "clone" and "repo" not in params:
            return False
        if action == "commit" and "message" not in params:
            return False
        return True

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action")
        repo = params.get("repo", "")
        message = params.get("message", "")
        workdir = params.get("workdir", "")
        branch = params.get("branch", "")
        commit_hash = params.get("commit_hash", "")

        commands = {
            "status": ["git", "status", "--porcelain"],
            "pull": ["git", "pull"],
            "log": ["git", "log", "--oneline", "-10"],
            "commit": ["git", "add", "-A", "&&", "git", "commit", "-m", message],
            "push": ["git", "push"],
            "clone": ["git", "clone", repo],
            "checkout": ["git", "checkout"] + ([branch] if branch else []),
            "revert": ["git", "revert", "--no-edit"] + ([commit_hash] if commit_hash else []),
        }

        cmd = commands.get(action)
        if cmd is None:
            return {"success": False, "error": f"Unknown action: {action}"}

        # For commit, save current HEAD for rollback
        rollback_info = None
        if action == "commit" and workdir:
            rollback_info = await self._get_current_head(workdir)

        try:
            if action == "commit" and workdir:
                # Stage all changes
                stage_proc = await asyncio.create_subprocess_exec(
                    "git", "add", "-A",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=workdir or None,
                )
                await asyncio.wait_for(stage_proc.communicate(), timeout=30)

                # Commit
                proc = await asyncio.create_subprocess_exec(
                    "git", "commit", "-m", message,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=workdir or None,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)

                self._log_operation(action, workdir, rollback_info=rollback_info)

                return {
                    "success": proc.returncode == 0,
                    "stdout": stdout.decode("utf-8", errors="replace") if stdout else "",
                    "stderr": stderr.decode("utf-8", errors="replace") if stderr else "",
                    "exit_code": proc.returncode or 0,
                }
            else:
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=workdir or None,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)

                self._log_operation(action, workdir)

                return {
                    "success": proc.returncode == 0,
                    "stdout": stdout.decode("utf-8", errors="replace") if stdout else "",
                    "stderr": stderr.decode("utf-8", errors="replace") if stderr else "",
                    "exit_code": proc.returncode or 0,
                }
        except asyncio.TimeoutError:
            return {"success": False, "error": "Git operation timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _get_current_head(self, workdir: str) -> str | None:
        """Get current HEAD commit hash for rollback."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "rev-parse", "HEAD",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=workdir,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            if proc.returncode == 0 and stdout:
                return stdout.decode().strip()
        except Exception:
            pass
        return None

    async def rollback(self) -> None:
        """Rollback the last git operation."""
        if not self._operations_log:
            return

        last = self._operations_log.pop()
        op = last.get("operation")
        workdir = last.get("workdir", "")
        rollback_info = last.get("rollback_info")

        if not workdir:
            return

        try:
            if op == "commit" and rollback_info:
                # Reset to previous commit
                proc = await asyncio.create_subprocess_exec(
                    "git", "reset", "--hard", rollback_info,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=workdir,
                )
                await asyncio.wait_for(proc.communicate(), timeout=30)

        except Exception:
            pass  # Best-effort rollback

    async def cleanup(self) -> None:
        self._operations_log.clear()

    def _log_operation(self, operation: str, workdir: str, **kwargs: Any) -> None:
        self._operations_log.append({
            "operation": operation,
            "workdir": workdir,
            **kwargs,
        })
