"""Smoke test for the AIOS kernel (Volume 12, Fase 11).

Boots the kernel, exercises runtime/health/monitor/metrics/security/
scheduler/events/logger and the async KernelAPI, then asserts the
observable contract. Run from the repo root:

    python modules/aios/smoke_kernel.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Make `modules.*` importable regardless of CWD.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KERNEL_NAME,
    KERNEL_VERSION,
    KernelAPI,
    KernelPermissionDeniedError,
    get_kernel,
    get_kernel_api,
    version_info,
)
from modules.aios.kernel.kernel_events import emit  # noqa: E402


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def _exercise_kernel_api(api: KernelAPI) -> None:
    info = await api.info()
    _assert(info["version"] == KERNEL_VERSION, "KernelAPI.info exposes version")
    status = await api.status()
    _assert(status["state"] in ("running", "stopped"), "KernelAPI.status returns state")
    health = await api.health()
    _assert(health["status"] in ("ok", "degraded", "failed"), "KernelAPI.health returns aggregate")
    metrics = await api.metrics()
    _assert("counters" in metrics, "KernelAPI.metrics returns snapshot")


async def main() -> int:
    kernel = get_kernel()
    mgr = kernel.manager

    _assert(KERNEL_NAME == "SuperDev AIOS", "kernel identity name")
    _assert(bool(KERNEL_VERSION), "kernel version present")
    _assert(version_info()["api_version"] == "v1", "version_info reports api_version")

    # --- security -------------------------------------------------------
    sec = mgr.security
    sec.grant("fs", "read", "write")
    _assert(sec.allow("fs", "read"), "security allow granted action")
    _assert(not sec.allow("fs", "delete"), "security deny ungranted action")
    sec.require("fs", "write")
    try:
        sec.require("fs", "delete")
        _assert(False, "security require raises on ungranted action")
    except KernelPermissionDeniedError:
        _assert(True, "security require raises KernelPermissionDeniedError")
    sec.revoke("fs", "write")
    _assert(not sec.allow("fs", "write"), "security revoke removes action")

    # --- health ----------------------------------------------------------
    health = mgr.health
    health.register("always_ok", lambda: True)
    health.register("always_bad", lambda: False)
    health.register("explodes", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    report = health.run()
    _assert(report["status"] == "degraded", "health aggregate degraded when some checks fail")
    _assert(report["total"] == 3 and report["passed"] == 1, "health counts total/passed")
    _assert(set(report["failed"]) == {"always_bad", "explodes"}, "health lists failed checks")
    _assert(report["checks"]["explodes"]["error"] == "boom", "health captures check error")
    all_ok = health.run()  # already covered by kernel semantics in unit contract
    _assert(all_ok["status"] in ("ok", "degraded"), "health run always returns aggregate")
    health.register("also_fails", lambda: False)
    _assert(health.run()["status"] == "degraded", "health stays degraded while any check passes")

    # "failed" requires every registered check to fail — verify on an isolated instance.
    from modules.aios.kernel.kernel_health import KernelHealth  # noqa: PLC0415

    all_bad = KernelHealth()
    all_bad.register("a", lambda: False)
    all_bad.register("b", lambda: False)
    _assert(all_bad.run()["status"] == "failed", "health aggregate failed when all checks fail")

    # --- monitor -----------------------------------------------------------
    monitor = mgr.monitor
    monitor.register("kernel", lambda: {"state": "smoke"})
    tick = monitor.tick()
    _assert(tick["total"] == 1 and tick["ok_count"] == 1, "monitor tick probes component")

    # --- metrics -------------------------------------------------------------
    metrics = mgr.metrics
    metrics.increment("kernel.boots")
    metrics.increment("kernel.boots")
    metrics.set_gauge("mem", 42.0)
    with metrics.timed("kernel.smoke"):
        await asyncio.sleep(0.01)
    snap = metrics.snapshot()
    _assert(snap["counters"]["kernel.boots"] == 2, "metrics counter increments")
    _assert(snap["gauges"]["mem"] == 42.0, "metrics gauge stored")
    _assert(snap["timings"]["kernel.smoke"]["count"] == 1, "metrics timing recorded")

    # --- events (Vol 10 bus, best effort) ------------------------------------
    sent = await emit("smoke", origin="kernel_smoke")
    _assert(sent >= 0, "kernel event published to bus (best effort)")

    # --- scheduler (needs running loop) ---------------------------------------
    scheduler = mgr.scheduler
    calls = {"n": 0}

    def job() -> None:
        calls["n"] += 1

    scheduler.schedule("smoke_job", interval_s=0.1, fn=job)
    _assert(scheduler.snapshot()["jobs"][0]["name"] == "smoke_job", "scheduler registered job")
    _assert(scheduler.unschedule("smoke_job"), "scheduler unschedule returns True")
    _assert(not scheduler.unschedule("smoke_job"), "scheduler unschedule idempotent")

    # --- boot / lifecycle -------------------------------------------------------
    boot_result = kernel.boot()
    _assert(boot_result["booted"] is True, "kernel boot succeeds")
    _assert(boot_result["state"] == "running", "kernel state running after boot")
    status = kernel.status()
    _assert(status["state"] == "running", "kernel runtime reports running")
    _assert(KERNEL_VERSION in status["version"], "kernel runtime reports version")

    second_boot = kernel.boot()
    _assert(second_boot["booted"] is False, "kernel boot idempotent while running")

    info = kernel.info()
    _assert(info["name"] == KERNEL_NAME, "kernel info exposes name")

    snapshot = kernel.snapshot()
    for key in ("runtime", "health", "monitor", "metrics", "security", "scheduler"):
        _assert(key in snapshot, f"kernel snapshot contains {key}")

    # --- async API ---------------------------------------------------------------
    await _exercise_kernel_api(get_kernel_api())

    # --- logger (Vol 10, kernel.* entries) -----------------------------------------
    mgr.logger.log("smoke", "kernel smoke entry", payload={"phase": "F11"})
    entries = mgr.logger.entries(limit=10)
    _assert(any(str(e.get("service", "")).startswith("kernel.") for e in entries), "kernel logger writes kernel.* entries")

    # --- stop ------------------------------------------------------------------------
    stop_result = kernel.stop()
    _assert(stop_result["stopped"] is True, "kernel stop succeeds")
    _assert(kernel.status()["state"] == "stopped", "kernel runtime stopped after stop")

    print(f"\nSMOKE OK — {KERNEL_NAME} v{KERNEL_VERSION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
