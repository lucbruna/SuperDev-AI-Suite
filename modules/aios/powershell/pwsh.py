"""pwsh wrapper for the AIOS powershell runtime."""
from __future__ import annotations

from modules.aios.powershell.powershell_client import PowerShellClient


class Pwsh:
    """Runs scripts with PowerShell Core (pwsh); degrades when missing."""

    def __init__(self, client: PowerShellClient | None = None) -> None:
        self._client = client or PowerShellClient("pwsh")

    async def version(self) -> dict:
        return await self._client.version()

    async def exec(self, command: str) -> dict:
        return await self._client.exec(command)

    async def ping(self) -> bool:
        return await self._client.ping()


__all__ = ["Pwsh"]
