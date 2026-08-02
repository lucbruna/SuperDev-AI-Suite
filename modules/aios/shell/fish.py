"""fish wrapper for the AIOS shell runtime."""
from __future__ import annotations

from modules.aios.shell.shell_client import ShellClient


class Fish:
    """Runs scripts with the fish shell (degrades when fish is missing)."""

    def __init__(self, client: ShellClient | None = None) -> None:
        self._client = client or ShellClient("fish")

    async def version(self) -> dict:
        return await self._client.version()

    async def exec(self, script: str) -> dict:
        return await self._client.exec(script)

    async def ping(self) -> bool:
        return await self._client.ping()


__all__ = ["Fish"]
