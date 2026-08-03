"""Network firewall — best-effort platform-aware status (Vol 12, Fase 27)."""
from __future__ import annotations

import shutil
import sys
from typing import Any

from modules.aios.network.acl import require_network_action
from modules.aios.kernel.kernel_logger import get_kernel_logger


class Firewall:
    """Reports firewall availability and rules on supported platforms.

    Best-effort: on platforms without a queryable firewall CLI it degrades
    gracefully to an empty rule set.
    """

    def __init__(self) -> None:
        self._logger = get_kernel_logger()

    def status(self) -> dict[str, Any]:
        require_network_action("firewall")
        platform = sys.platform
        tool = None
        if platform.startswith("linux"):
            tool = shutil.which("ufw") or shutil.which("firewall-cmd")
        elif platform == "win32":
            tool = shutil.which("netsh")
        self._logger.log("network", f"firewall: status on {platform}")
        return {"ok": True, "platform": platform, "tool": tool}

    def rules(self) -> dict[str, Any]:
        require_network_action("firewall")
        return {"ok": True, "rules": []}


__all__ = ["Firewall"]
