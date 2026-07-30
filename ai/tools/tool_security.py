from __future__ import annotations

from typing import Any


class ToolSecurity:
    """Security layer for tool execution."""

    def __init__(self) -> None:
        self._blocked_commands: list[str] = []
        self._blocked_paths: list[str] = []
        self._allowed_hosts: list[str] = []
        self._audit_log: list[dict[str, Any]] = []

    def block_command(self, command: str) -> str:
        self._blocked_commands.append(command.lower())
        return command

    def unblock_command(self, command: str) -> bool:
        cmd = command.lower()
        if cmd in self._blocked_commands:
            self._blocked_commands.remove(cmd)
            return True
        return False

    def block_path(self, path: str) -> str:
        self._blocked_paths.append(path)
        return path

    def allow_host(self, host: str) -> str:
        self._allowed_hosts.append(host)
        return host

    def is_command_blocked(self, command: str) -> bool:
        return any(b in command.lower() for b in self._blocked_commands)

    def is_path_blocked(self, path: str) -> bool:
        return any(path.startswith(b) for b in self._blocked_paths)

    def is_host_allowed(self, host: str) -> bool:
        if not self._allowed_hosts:
            return True
        return any(host == a or host.endswith(f".{a}") for a in self._allowed_hosts)

    def log_access(self, entry: dict[str, Any]) -> None:
        self._audit_log.append(entry)

    @property
    def audit_log(self) -> list[dict[str, Any]]:
        return list(self._audit_log)

    def to_dict(self) -> dict[str, Any]:
        return {
            "blocked_commands": list(self._blocked_commands),
            "blocked_paths": list(self._blocked_paths),
            "allowed_hosts": list(self._allowed_hosts),
            "audit_count": len(self._audit_log),
        }
