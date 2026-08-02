"""Windows PowerShell 5.1 host wrapper for the AIOS powershell runtime."""
from __future__ import annotations

from modules.aios.powershell.powershell_client import PowerShellClient


class WindowsTerminal:
    """Runs scripts with the classic Windows PowerShell host (powershell.exe).

    Available on every Windows host; useful as a fallback when pwsh is not
    installed (e.g. Windows PowerShell 5.1).
    """

    def __init__(self, client: PowerShellClient | None = None) -> None:
        self._client = client or PowerShellClient("powershell")

    async def version(self) -> dict:
        return await self._client.version()

    async def exec(self, command: str) -> dict:
        return await self._client.exec(command)

    async def ping(self) -> bool:
        return await self._client.ping()


__all__ = ["WindowsTerminal"]
