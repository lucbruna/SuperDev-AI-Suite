"""PowerShell package — pwsh + Windows PowerShell facade (Vol 12, Fase 24)."""
from __future__ import annotations

from modules.aios.powershell.powershell_client import (
    PowerShellClient,
    PowerShellUnavailableError,
    require_powershell_action,
)
from modules.aios.powershell.powershell_runtime import (
    PowerShellRuntime,
    get_powershell_runtime,
)
from modules.aios.powershell.pwsh import Pwsh
from modules.aios.powershell.windows_terminal import WindowsTerminal

__all__ = [
    "PowerShellClient",
    "PowerShellRuntime",
    "PowerShellUnavailableError",
    "get_powershell_runtime",
    "Pwsh",
    "require_powershell_action",
    "WindowsTerminal",
]
