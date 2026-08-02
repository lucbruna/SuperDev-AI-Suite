"""Smoke test for the AIOS docker integration (Volume 12, Fase 14).

Exercises the ACL, client ping/version, image pull/list, container run/logs,
network and volume lifecycle, cleanup and the runtime snapshot against the
real local docker daemon. Skips gracefully when docker is unavailable.

Run from repo root:

    python modules/aios/smoke_docker.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    DockerRuntime,
    KernelPermissionDeniedError,
    get_docker_runtime,
    get_kernel_security,
)

DOCKER_ACTIONS = (
    "run",
    "pull",
    "build",
    "remove",
    "network",
    "volume",
    "prune",
    "logs",
    "inspect",
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    runtime: DockerRuntime = get_docker_runtime()

    if not await runtime.available():
        print("SKIP: docker unavailable")
        return 0

    # --- ACL ---------------------------------------------------------------------
    security = get_kernel_security()
    security.grant("docker", *DOCKER_ACTIONS)
    security.revoke("docker", "pull")
    try:
        await runtime.images.pull("alpine:3.19")
        _assert(False, "ACL denies revoked pull action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked pull action")
    security.grant("docker", "pull")

    # --- client -------------------------------------------------------------------
    version = await runtime.client.version()
    _assert(version.get("Server") is not None, "client version reports a server")

    # --- images ---------------------------------------------------------------------
    listed = await runtime.images.list_images()
    _assert(isinstance(listed, list), "images.list returns a list")
    pull = await runtime.images.pull("alpine:3.19")
    _assert(pull["ok"], "images.pull pulls alpine:3.19")

    # --- container run + logs -----------------------------------------------------------
    run = await runtime.containers.run(
        "alpine:3.19",
        name="aios-smoke",
        command=["echo", "hello-aios"],
        remove=False,
    )
    _assert(run["ok"], "containers.run executes echo")
    logs = await runtime.logs.logs("aios-smoke", tail=10)
    _assert("hello-aios" in logs, "logs contain the echoed output")
    removed = await runtime.containers.remove("aios-smoke", force=True)
    _assert(removed["ok"], "containers.remove cleans the smoke container")

    # --- network -------------------------------------------------------------------------
    net = await runtime.network.create("aios-smoke-net")
    _assert(net["ok"], "network.create works")
    nets = await runtime.network.list_networks()
    _assert(any(n.get("Name") == "aios-smoke-net" for n in nets), "network appears in list")
    net_rm = await runtime.network.remove("aios-smoke-net")
    _assert(net_rm["ok"], "network.remove works")

    # --- volume ----------------------------------------------------------------------------
    vol = await runtime.volumes.create("aios-smoke-vol")
    _assert(vol["ok"], "volume.create works")
    vols = await runtime.volumes.list_volumes()
    _assert(any(v.get("Name") == "aios-smoke-vol" for v in vols), "volume appears in list")
    vol_rm = await runtime.volumes.remove("aios-smoke-vol")
    _assert(vol_rm["ok"], "volume.remove works")

    # --- cleanup -----------------------------------------------------------------------------
    stopped = await runtime.cleanup.remove_stopped()
    _assert(stopped["ok"], "cleanup.remove_stopped works")

    # --- snapshot ---------------------------------------------------------------------------
    snap = await runtime.snapshot()
    for key in ("available", "version", "images", "containers", "networks", "volumes"):
        _assert(key in snap, f"snapshot exposes {key}")
    _assert(snap["available"] is True, "snapshot reports docker available")

    print("\nSMOKE OK — AIOS Docker")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
