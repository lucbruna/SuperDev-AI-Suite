"""zsh wrapper for the AIOS shell runtime."""
from __future__ import annotations

from modules.aios.shell.shell_client import ShellClient


class Zsh:
    """Runs scripts with the zsh shell (degrades when zsh is missing)."""

    def __init__(self, client: ShellClient | None = None) -> None:
        self._client = client or ShellClient("zsh")

    async def version(self) -> dict:
        return await self._client.version()

    async def exec(self, script: str) -> dict:
        return await self._client.exec(script)

    async def ping(self) -> bool:
        return await self._client.ping()


__all__ = ["Zsh"]
