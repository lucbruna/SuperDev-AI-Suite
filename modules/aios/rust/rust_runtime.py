"""Rust runtime — facade over the cargo toolchain (Vol 12, Fase 21)."""
from __future__ import annotations

from typing import Any

from modules.aios.rust.cargo import CargoCommands
from modules.aios.rust.clippy import Clippy
from modules.aios.rust.rust_client import CargoClient, RustUnavailableError


class RustRuntime:
    """Facade over cargo build/test/clippy.

    Stateless: managers are CLI wrappers. ``close`` is a no-op. When cargo is
    not installed every operation raises RustUnavailableError and ``snapshot``
    degrades gracefully.
    """

    def __init__(self) -> None:
        self.client = CargoClient()
        self.cargo = CargoCommands(self.client)
        self.clippy = Clippy(self.client)

    async def available(self) -> bool:
        return await self.client.ping()

    async def version(self) -> dict[str, Any]:
        return await self.client.version()

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort inventory; degrades to None when cargo is missing."""
        version = None
        try:
            version = (await self.client.version())["version"]
        except RustUnavailableError:
            version = None
        return {"cargo": version}

    async def close(self) -> None:
        """No-op — the rust runtime is stateless."""


_rust_runtime: RustRuntime | None = None


def get_rust_runtime() -> RustRuntime:
    global _rust_runtime
    if _rust_runtime is None:
        _rust_runtime = RustRuntime()
    return _rust_runtime


__all__ = ["RustRuntime", "get_rust_runtime"]
