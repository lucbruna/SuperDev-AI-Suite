"""PowerShell runtime — facade over pwsh and Windows PowerShell (Vol 12, Fase 24)."""
from __future__ import annotations

from typing import Any

from modules.aios.powershell.powershell_client import PowerShellUnavailableError
from modules.aios.powershell.pwsh import Pwsh
from modules.aios.powershell.windows_terminal import WindowsTerminal


class PowerShellRuntime:
    """Facade over pwsh (Core) and the classic Windows PowerShell host.

    Stateless: wrappers are CLI-based. ``close`` is a no-op. Hosts that are
    not installed (pwsh) degrade via PowerShellUnavailableError.
    """

    def __init__(self) -> None:
        self.pwsh = Pwsh()
        self.windows_terminal = WindowsTerminal()

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort inventory; each host degrades to None on error."""
        inventory: dict[str, Any] = {}
        for name, host in (("pwsh", self.pwsh), ("windows_powershell", self.windows_terminal)):
            try:
                inventory[name] = (await host.version())["version"]
            except PowerShellUnavailableError:
                inventory[name] = None
        return inventory

    async def close(self) -> None:
        """No-op — the powershell runtime is stateless."""


_powershell_runtime: PowerShellRuntime | None = None


def get_powershell_runtime() -> PowerShellRuntime:
    global _powershell_runtime
    if _powershell_runtime is None:
        _powershell_runtime = PowerShellRuntime()
    return _powershell_runtime


__all__ = ["PowerShellRuntime", "get_powershell_runtime"]
