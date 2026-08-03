"""Smoke test for the AIOS filesystem runtime (Volume 12, Fase 26).

Exercises ACL, real copy/move/delete/search/checksum/compression/permissions
and the polling watcher against a temporary directory. Run from repo root:

    python modules/aios/smoke_filesystem.py
"""
from __future__ import annotations

import asyncio
import hashlib
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    FilesystemRuntime,
    KernelPermissionDeniedError,
    get_filesystem_runtime,
    get_kernel_security,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: FilesystemRuntime = get_filesystem_runtime()

    security = get_kernel_security()
    security.grant(
        "filesystem",
        "copy",
        "move",
        "delete",
        "search",
        "checksum",
        "compress",
        "permissions",
        "watch",
    )

    # --- ACL ----------------------------------------------------------------------
    security.revoke("filesystem", "copy")
    try:
        runtime.copy.copy_file("x", "y")
        _assert(False, "ACL denies revoked copy action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked copy action")
    security.grant("filesystem", "copy")

    tmp = Path(tempfile.mkdtemp(prefix="aios_fs_"))
    try:
        # --- copy ------------------------------------------------------------------
        a = tmp / "a.txt"
        a.write_text("hello aios", encoding="utf-8")
        res = runtime.copy.copy_file(str(a), str(tmp / "b.txt"))
        _assert(res["ok"] and (tmp / "b.txt").read_text(encoding="utf-8") == "hello aios", "copy_file copies content")

        sub = tmp / "sub"
        sub.mkdir()
        (sub / "d.txt").write_text("data", encoding="utf-8")
        res = runtime.copy.copy_dir(str(sub), str(tmp / "sub_copy"))
        _assert(res["ok"] and (tmp / "sub_copy" / "d.txt").exists(), "copy_dir copies a directory")

        # --- move ------------------------------------------------------------------
        res = runtime.move.move(str(tmp / "b.txt"), str(tmp / "moved.txt"))
        _assert(res["ok"] and (tmp / "moved.txt").exists() and not (tmp / "b.txt").exists(), "move relocates a file")

        # --- search ----------------------------------------------------------------
        src = tmp / "src"
        src.mkdir()
        (src / "x.py").write_text("print(1)", encoding="utf-8")
        (tmp / "y.md").write_text("# hi", encoding="utf-8")
        hits = runtime.search.find(str(tmp), ext=".py")
        _assert(any(h["path"].endswith("x.py") for h in hits), "search finds by extension")
        hits = runtime.search.find(str(tmp), name="y")
        _assert(any(h["path"].endswith("y.md") for h in hits), "search finds by name")

        # --- checksum --------------------------------------------------------------
        res = runtime.checksum.hash_file(str(a))
        _assert(res["ok"] and res["hexdigest"] == hashlib.sha256(b"hello aios").hexdigest(), "checksum matches known digest")
        _assert(runtime.checksum.hash_bytes(b"hello") == hashlib.sha256(b"hello").hexdigest(), "hash_bytes matches hashlib")

        # --- compression -----------------------------------------------------------
        res = runtime.compression.zip(str(src), str(tmp / "src.zip"))
        _assert(res["ok"], "zip creates an archive")
        res = runtime.compression.unzip(str(tmp / "src.zip"), str(tmp / "src_out"))
        _assert(res["ok"] and (tmp / "src_out" / "x.py").exists(), "unzip restores files")

        # --- permissions -----------------------------------------------------------
        res = runtime.permissions.read_mode(str(a))
        _assert(res["ok"] and isinstance(res["mode"], str), "read_mode reports a mode")
        res = runtime.permissions.chmod(str(a), 0o600)
        _assert(res["ok"], "chmod applies a mode")

        # --- watcher ---------------------------------------------------------------
        res = runtime.watcher.watch(str(src))
        _assert(res["ok"], "watcher starts on a directory")
        (src / "new.txt").write_text("new", encoding="utf-8")
        changes = runtime.watcher.changes()
        _assert("new.txt" in changes["created"], "watcher detects a created file")

        # --- delete ----------------------------------------------------------------
        res = runtime.delete.delete_file(str(tmp / "moved.txt"))
        _assert(res["ok"] and not (tmp / "moved.txt").exists(), "delete_file removes a file")
        res = runtime.delete.delete_dir(str(src), recursive=True)
        _assert(res["ok"] and not src.exists(), "delete_dir removes a directory")

        # --- snapshot --------------------------------------------------------------
        snap = await runtime.snapshot()
        _assert("cwd" in snap and snap["available"] is True, "snapshot exposes filesystem info")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\nSMOKE OK — AIOS Filesystem")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
