"""Cargo commands for the AIOS rust runtime (Vol 12, Fase 21)."""
from __future__ import annotations

from typing import Any

from modules.aios.rust.rust_client import (
    CargoClient,
    RustUnavailableError,
    require_rust_action,
)


class CargoCommands:
    """Runs cargo lifecycle commands: init, build, test, run, add."""

    def __init__(self, client: CargoClient) -> None:
        self._client = client

    async def init(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_rust_action("cargo")
        code, out, err = await self._client._run(["init", "--name", "aios"], cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def build(self, *, cwd: str | None = None, release: bool = False) -> dict[str, Any]:
        require_rust_action("cargo")
        args = ["build"]
        if release:
            args.append("--release")
        code, out, err = await self._client._run(args, cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def test(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_rust_action("cargo")
        code, out, err = await self._client._run(["test"], cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def run(self, *, cwd: str | None = None, args: list[str] | None = None) -> dict[str, Any]:
        require_rust_action("cargo")
        cmd = ["run", "--"]
        if args:
            cmd += args
        code, out, err = await self._client._run(cmd, cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def add(self, crate: str, *, cwd: str | None = None) -> dict[str, Any]:
        require_rust_action("cargo")
        code, out, err = await self._client._run(["add", crate], cwd=cwd)
        return {"ok": code == 0, "stdout": out.strip(), "stderr": err.strip()}

    async def metadata(self, *, cwd: str | None = None) -> dict[str, Any]:
        require_rust_action("cargo")
        code, out, err = await self._client._run(["metadata", "--no-deps", "--format-version", "1"], cwd=cwd)
        if code != 0:
            raise RustUnavailableError(f"cargo metadata failed: {err.strip() or out.strip()}")
        import json

        try:
            return json.loads(out)
        except json.JSONDecodeError:
            return {"packages": []}


__all__ = ["CargoCommands"]
