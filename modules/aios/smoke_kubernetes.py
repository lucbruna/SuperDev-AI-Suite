"""Smoke test for the AIOS kubernetes integration (Volume 12, Fase 16).

kubectl is a client-only tool: with a cluster context it exercises real
resources; without one it verifies the graceful-degradation path
(available()==False, version() raises, snapshot reports unavailable) plus the
ACL. Run from repo root:

    python modules/aios/smoke_kubernetes.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KernelPermissionDeniedError,
    KubernetesRuntime,
    KubernetesUnavailableError,
    get_kernel_security,
    get_kubernetes_runtime,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: KubernetesRuntime = get_kubernetes_runtime()

    security = get_kernel_security()
    security.grant(
        "kubernetes",
        "cluster",
        "namespace",
        "job",
        "deployment",
        "service",
        "ingress",
        "configmap",
        "secret",
        "volume",
    )

    if await runtime.available():
        version = await runtime.client.version()
        _assert(isinstance(version, dict), "client version returns a dict")
        snap = await runtime.snapshot()
        _assert(snap["available"] is True, "snapshot reports cluster available")
        print("\nSMOKE OK — AIOS Kubernetes")
        return 0

    # --- graceful degradation (no cluster context) ----------------------------------
    print("  note - no cluster context; verifying graceful degradation")
    _assert(await runtime.available() is False, "available() is False without a cluster")

    try:
        await runtime.client.version()
        _assert(False, "version() raises when cluster unreachable")
    except KubernetesUnavailableError:
        _assert(True, "version() raises when cluster unreachable")

    snap = await runtime.snapshot()
    _assert(snap["available"] is False, "snapshot reports cluster unavailable")
    _assert(snap["version"] == {}, "snapshot version degrades to {}")

    security.revoke("kubernetes", "job")
    try:
        await runtime.jobs.list()
        _assert(False, "ACL denies revoked job action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked job action")
    security.grant("kubernetes", "job")

    print("\nSMOKE OK — AIOS Kubernetes (degradation path)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
