"""NuGet package management for the AIOS dotnet runtime."""
from __future__ import annotations

from typing import Any

from modules.aios.dotnet.dotnet_client import (
    DotnetClient,
    require_dotnet_action,
)
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class NugetManager:
    """Adds, restores and lists packages via the dotnet CLI."""

    def __init__(self, client: DotnetClient) -> None:
        self._client = client
        self._metrics = get_kernel_metrics()

    async def add(
        self, package: str, *, version: str | None = None, cwd: str | None = None
    ) -> dict[str, Any]:
        require_dotnet_action("nuget")
        args = ["add", "package", package]
        if version:
            args += ["--version", version]
        code, out, err = await self._client._run(args, cwd=cwd)
        self._metrics.increment("dotnet.nuget.add")
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def restore(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_dotnet_action("nuget")
        code, out, err = await self._client._run(["restore"], cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def list_sources(self) -> dict[str, Any]:
        require_dotnet_action("nuget")
        code, out, err = await self._client._run(
            ["nuget", "list", "source"], timeout_s=60.0
        )
        if code != 0:
            return {"ok": False, "sources": [], "stderr": err.strip()}
        sources = [
            line.strip().lstrip("+").strip()
            for line in out.splitlines()
            if "https://" in line or "http://" in line
        ]
        return {"ok": True, "sources": sources}


__all__ = ["NugetManager"]
