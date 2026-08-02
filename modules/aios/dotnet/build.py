"""dotnet build/test wrapper for the AIOS dotnet runtime."""
from __future__ import annotations

from typing import Any

from modules.aios.dotnet.dotnet_client import (
    DotnetClient,
    require_dotnet_action,
)
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class DotnetBuild:
    """Builds and tests .NET solutions/projects."""

    def __init__(self, client: DotnetClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def build(
        self, *, cwd: str | None = None, configuration: str = "Debug"
    ) -> dict[str, Any]:
        require_dotnet_action("build")
        args = ["build", "--configuration", configuration]
        code, out, err = await self._client._run(args, cwd=cwd)
        self._metrics.increment("dotnet.build")
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def test(
        self, *, cwd: str | None = None, configuration: str = "Debug"
    ) -> dict[str, Any]:
        require_dotnet_action("test")
        args = ["test", "--configuration", configuration]
        code, out, err = await self._client._run(args, cwd=cwd)
        self._metrics.increment("dotnet.test")
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}


__all__ = ["DotnetBuild"]
