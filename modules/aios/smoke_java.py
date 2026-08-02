"""Smoke test for the AIOS java runtime (Volume 12, Fase 19).

Exercises ACL, JDK version, a real javac compile + java run and gradle/maven
graceful degradation. Run from repo root:

    python modules/aios/smoke_java.py
"""
from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    GradleUnavailableError,
    JavaRuntime,
    KernelPermissionDeniedError,
    MavenUnavailableError,
    get_java_runtime,
    get_kernel_security,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: JavaRuntime = get_java_runtime()

    security = get_kernel_security()
    security.grant("java", "inspect", "compile", "run", "gradle", "maven")

    # --- ACL ----------------------------------------------------------------------
    security.revoke("java", "compile")
    try:
        await runtime.client.compile(["A.java"], output="out")
        _assert(False, "ACL denies revoked compile action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked compile action")
    security.grant("java", "compile")

    # --- JDK ----------------------------------------------------------------------
    version = await runtime.client.version()
    _assert(version.get("version"), "java reports a version")

    # --- real compile + run ---------------------------------------------------------
    with tempfile.TemporaryDirectory(prefix="aios-java-") as tmp:
        src = Path(tmp)
        source = src / "Hello.java"
        source.write_text(
            "public class Hello { public static void main(String[] a) { "
            "System.out.println(\"hello aios\"); } }\n",
            encoding="utf-8",
        )
        compiled = src / "classes"
        compiled.mkdir()
        result = await runtime.client.compile([str(source)], output=str(compiled))
        _assert(result["ok"], "javac compiles a source file")
        run = await runtime.client.run("Hello", classpath=str(compiled))
        _assert(run["ok"] and "hello aios" in run["stdout"], "java runs the compiled class")

    # --- gradle / maven degradation ---------------------------------------------------
    try:
        await runtime.gradle.version()
        _assert(False, "gradle unavailable raises GradleUnavailableError")
    except GradleUnavailableError:
        _assert(True, "gradle unavailable raises GradleUnavailableError")
    try:
        await runtime.maven.version()
        _assert(False, "maven unavailable raises MavenUnavailableError")
    except MavenUnavailableError:
        _assert(True, "maven unavailable raises MavenUnavailableError")

    # --- snapshot ----------------------------------------------------------------------
    snap = await runtime.snapshot()
    _assert(
        "java" in snap and "gradle" in snap and "maven" in snap,
        "snapshot exposes tool inventory",
    )

    print("\nSMOKE OK — AIOS Java")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
