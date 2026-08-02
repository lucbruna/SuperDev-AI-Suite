"""Smoke test for the AIOS node runtime (Volume 12, Fase 18).

Exercises ACL, node/npm/pnpm/bun versions, yarn graceful degradation and a
real npm install + vitest run inside a temp project. Run from repo root:

    python modules/aios/smoke_node.py
"""
from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KernelPermissionDeniedError,
    NodeRuntime,
    YarnUnavailableError,
    get_kernel_security,
    get_node_runtime,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: NodeRuntime = get_node_runtime()

    security = get_kernel_security()
    security.grant("node", "node", "run", "npm", "pnpm", "yarn", "bun", "vitest", "jest")

    # --- ACL ----------------------------------------------------------------------
    security.revoke("node", "npm")
    try:
        await runtime.npm.version()
        _assert(False, "ACL denies revoked npm action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked npm action")
    security.grant("node", "npm")

    # --- runtimes -----------------------------------------------------------------
    node = await runtime.node.version()
    _assert(node.get("version"), "node reports a version")
    npm = await runtime.npm.version()
    _assert(npm.get("version"), "npm reports a version")
    pnpm = await runtime.pnpm.version()
    _assert(pnpm.get("version"), "pnpm reports a version")
    bun = await runtime.bun.version()
    _assert(bun.get("version"), "bun reports a version")
    try:
        await runtime.yarn.version()
        _assert(False, "yarn unavailable raises YarnUnavailableError")
    except YarnUnavailableError:
        _assert(True, "yarn unavailable raises YarnUnavailableError")

    # --- package manager facade ---------------------------------------------------
    _assert(runtime.packages.name in ("npm", "pnpm", "yarn", "bun"), "package manager auto-detects")

    # --- real project: npm install + vitest run -------------------------------------
    with tempfile.TemporaryDirectory(prefix="aios-node-") as tmp:
        project = Path(tmp)
        (project / "package.json").write_text(
            '{"name":"aios-smoke","private":true,"type":"module"}', encoding="utf-8"
        )
        install = await runtime.npm.install("left-pad", cwd=str(project))
        _assert(install["ok"], "npm installs a package")
        _assert((project / "node_modules" / "left-pad").exists(), "installed package on disk")

        test_file = project / "smoke.test.mjs"
        test_file.write_text(
            "import { describe, it, expect } from 'vitest';\n"
            "describe('smoke', () => { it('works', () => { expect(6 * 7).toBe(42); }); });\n",
            encoding="utf-8",
        )
        vitest_install = await runtime.npm.install("vitest", cwd=str(project), dev=True)
        _assert(vitest_install["ok"], "vitest installs in the project")
        result = await runtime.vitest.run([str(test_file)], cwd=str(project))
        _assert(result["ok"], "vitest runs and passes the smoke test")

    # --- snapshot ----------------------------------------------------------------------
    snap = await runtime.snapshot()
    _assert(
        "node" in snap and "npm" in snap and "pnpm" in snap and "yarn" in snap,
        "snapshot exposes tool inventory",
    )

    print("\nSMOKE OK — AIOS Node")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
