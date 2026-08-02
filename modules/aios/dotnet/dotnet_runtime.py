"""Dotnet runtime — facade over the .NET CLI (Vol 12, Fase 22)."""
from __future__ import annotations

from typing import Any

from modules.aios.dotnet.build import DotnetBuild
from modules.aios.dotnet.dotnet_client import DotnetClient, DotnetUnavailableError
from modules.aios.dotnet.nuget import NugetManager


class DotnetRuntime:
    """Facade over dotnet new/build/test/run plus NuGet.

    Stateless: managers are CLI wrappers. ``close`` is a no-op. When dotnet
    is not installed every operation raises DotnetUnavailableError.
    """

    def __init__(self) -> None:
        self.client = DotnetClient()
        self.nuget = NugetManager(self.client)
        self.build = DotnetBuild(self.client)

    async def available(self) -> bool:
        return await self.client.ping()

    async def version(self) -> dict[str, Any]:
        return await self.client.version()

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort inventory; degrades to None when dotnet is missing."""
        version = None
        try:
            version = (await self.client.version())["version"]
        except DotnetUnavailableError:
            version = None
        return {"dotnet": version}

    async def close(self) -> None:
        """No-op — the dotnet runtime is stateless."""


_dotnet_runtime: DotnetRuntime | None = None


def get_dotnet_runtime() -> DotnetRuntime:
    global _dotnet_runtime
    if _dotnet_runtime is None:
        _dotnet_runtime = DotnetRuntime()
    return _dotnet_runtime


__all__ = ["DotnetRuntime", "get_dotnet_runtime"]
