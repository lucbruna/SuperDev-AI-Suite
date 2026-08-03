"""Network gRPC — tooling availability check (Vol 12, Fase 27)."""
from __future__ import annotations

import shutil
from typing import Any

from modules.aios.network.acl import require_network_action
from modules.aios.kernel.kernel_logger import get_kernel_logger


class Grpc:
    """Reports gRPC tooling availability, degrading gracefully when absent."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()

    def available(self) -> dict[str, Any]:
        require_network_action("grpc")
        tool = shutil.which("grpcurl")
        self._logger.log("network", f"grpc: tool={tool}")
        return {"ok": True, "available": tool is not None, "tool": tool}


__all__ = ["Grpc"]
