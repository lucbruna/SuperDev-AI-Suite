"""Dotnet package — .NET toolchain facade (Vol 12, Fase 22)."""
from __future__ import annotations

from modules.aios.dotnet.build import DotnetBuild
from modules.aios.dotnet.dotnet_client import (
    DotnetClient,
    DotnetUnavailableError,
    require_dotnet_action,
)
from modules.aios.dotnet.dotnet_runtime import DotnetRuntime, get_dotnet_runtime
from modules.aios.dotnet.nuget import NugetManager

__all__ = [
    "DotnetBuild",
    "DotnetClient",
    "DotnetRuntime",
    "DotnetUnavailableError",
    "get_dotnet_runtime",
    "NugetManager",
    "require_dotnet_action",
]
