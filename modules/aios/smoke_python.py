"""Smoke test for the AIOS python runtime (Volume 12, Fase 17).

Exercises requirements round-trip, venv create/pip-install/pytest inside a
temp venv, uv availability and poetry graceful degradation. Run from repo
root:

    python modules/aios/smoke_python.py
"""
from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KernelPermissionDeniedError,
    PoetryUnavailableError,
    PythonRuntime,
    get_kernel_security,
    get_python_runtime,
    parse_requirements,
    render_requirements,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: PythonRuntime = get_python_runtime()

    security = get_kernel_security()
    security.grant("python", "venv", "pip", "pytest", "uv", "poetry")

    # --- requirements (pure, no subprocess) --------------------------------------
    reqs = parse_requirements("requests==2.32.0  # http\nflask>=3.0\n\n# comment")
    _assert(len(reqs) == 2, "requirements parse skips comments/blanks")
    _assert(reqs[0].name == "requests" and reqs[0].specifier == "==2.32.0", "requirements keep specifiers")
    rendered = render_requirements(reqs)
    _assert("requests==2.32.0" in rendered and "flask>=3.0" in rendered, "requirements render round-trips")

    # --- ACL ----------------------------------------------------------------------
    security.revoke("python", "pip")
    try:
        await runtime.pip.list()
        _assert(False, "ACL denies revoked pip action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked pip action")
    security.grant("python", "pip")

    with tempfile.TemporaryDirectory(prefix="aios-py-") as tmp:
        venv_dir = Path(tmp) / "venv"
        # --- venv --------------------------------------------------------------------
        created = await runtime.venvs.create(venv_dir)
        _assert(created["ok"], "venv creates a virtual environment")
        _assert(await runtime.venvs.exists(venv_dir), "venv python executable exists")

        # --- pip inside the venv -----------------------------------------------------------
        venv_pip = PipManagerForSmoke(runtime, venv_dir)
        pkgs = await venv_pip.list()
        _assert(isinstance(pkgs, list), "pip list returns a list")
        install = await venv_pip.install("six")
        _assert(install["ok"], "pip installs a small package")
        pkgs_after = await venv_pip.list()
        _assert(any(p.get("name") == "six" for p in pkgs_after), "installed package appears in list")

        # --- pytest inside the venv ----------------------------------------------------------
        test_file = Path(tmp) / "test_smoke.py"
        test_file.write_text("def test_ok():\n    assert 6 * 7 == 42\n", encoding="utf-8")
        result = await runtime.pytest.run([str(test_file)], cwd=tmp)
        _assert(result["ok"] and result["passed"] >= 1, "pytest runs and passes the smoke test")

        # --- teardown -------------------------------------------------------------------------
        removed = await runtime.venvs.remove(venv_dir)
        _assert(removed["ok"], "venv removal works")

    # --- uv / poetry ---------------------------------------------------------------------------
    uv = await runtime.uv.version()
    _assert(uv.get("version"), "uv reports a version (installed)")
    try:
        await runtime.poetry.version()
        _assert(False, "poetry unavailable raises PoetryUnavailableError")
    except PoetryUnavailableError:
        _assert(True, "poetry unavailable raises PoetryUnavailableError")

    # --- snapshot ------------------------------------------------------------------------------
    snap = await runtime.snapshot()
    _assert("python" in snap and "uv" in snap and "poetry" in snap, "snapshot exposes tool inventory")

    print("\nSMOKE OK — AIOS Python")
    return 0


class PipManagerForSmoke:
    """Pip manager bound to the temp venv's interpreter."""

    def __init__(self, runtime: PythonRuntime, venv_dir: Path) -> None:
        from modules.aios.python.venv_manager import VenvManager

        python_bin = VenvManager.python_bin(venv_dir)
        self._manager = type(runtime.pip)(python=python_bin)

    async def list(self) -> list[dict]:
        return await self._manager.list()

    async def install(self, package: str) -> dict:
        return await self._manager.install(package)


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
