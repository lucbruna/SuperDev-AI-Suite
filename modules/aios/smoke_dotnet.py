"""Smoke test for the AIOS dotnet runtime (Volume 12, Fase 22).

Exercises ACL, dotnet version, a real ``dotnet new console`` + build + run
cycle and nuget source listing. Run from repo root:

    python modules/aios/smoke_dotnet.py
"""
from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    DotnetRuntime,
    KernelPermissionDeniedError,
    get_dotnet_runtime,
    get_kernel_security,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: DotnetRuntime = get_dotnet_runtime()

    security = get_kernel_security()
    security.grant("dotnet", "inspect", "new", "run", "build", "test", "nuget")

    # --- ACL ----------------------------------------------------------------------
    security.revoke("dotnet", "nuget")
    try:
        await runtime.nuget.list_sources()
        _assert(False, "ACL denies revoked nuget action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked nuget action")
    security.grant("dotnet", "nuget")

    # --- version ---------------------------------------------------------------------
    version = await runtime.version()
    _assert(version.get("version"), "dotnet reports a version")

    # --- nuget sources -----------------------------------------------------------------
    sources = await runtime.nuget.list_sources()
    _assert(sources.get("ok") and len(sources["sources"]) > 0, "nuget lists package sources")

    # --- real new + build + run --------------------------------------------------------
    with tempfile.TemporaryDirectory(prefix="aios-dotnet-") as tmp:
        project = Path(tmp) / "Hello"
        created = await runtime.client.new("console", "Hello", output=str(project))
        _assert(created["ok"], "dotnet new creates a console project")
        _assert((project / "Hello.csproj").exists(), "csproj exists on disk")

        built = await runtime.build.build(cwd=str(project))
        _assert(built["ok"], "dotnet build compiles the project")

        run = await runtime.client.run(cwd=str(project))
        _assert(run["ok"], "dotnet run executes without errors")

    # --- snapshot ----------------------------------------------------------------------
    snap = await runtime.snapshot()
    _assert("dotnet" in snap and snap["dotnet"], "snapshot exposes the dotnet version")

    print("\nSMOKE OK — AIOS Dotnet")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
