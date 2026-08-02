"""Smoke test for the AIOS runtime (Volume 12, Fase 12).

Exercises session lifecycle, the state machine, the executor (sync + async
tasks), cleanup, metrics and the RuntimeEngine facade. Run from repo root:

    python modules/aios/smoke_runtime.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    RuntimeEngine,
    RuntimeState,
    get_runtime_engine,
)
from modules.aios.runtime.runtime_state import snapshot_of  # noqa: E402


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


def _sync_task(x: int) -> int:
    return x * 2


async def _async_task(x: int) -> int:
    await asyncio.sleep(0.01)
    return x + 1


async def _failing_task() -> None:
    raise RuntimeError("boom")


async def main() -> int:
    engine: RuntimeEngine = get_runtime_engine()

    # --- state machine -------------------------------------------------------
    _assert(
        RuntimeState.PENDING.can_transition_to(RuntimeState.RUNNING),
        "state pending -> running allowed",
    )
    _assert(
        RuntimeState.RUNNING.can_transition_to(RuntimeState.SUCCEEDED),
        "state running -> succeeded allowed",
    )
    _assert(
        not RuntimeState.SUCCEEDED.can_transition_to(RuntimeState.RUNNING),
        "state succeeded -> running rejected",
    )
    _assert(
        not RuntimeState.PENDING.can_transition_to(RuntimeState.SUCCEEDED),
        "state pending -> succeeded rejected",
    )
    try:
        RuntimeState.PENDING.transition(RuntimeState.SUCCEEDED)
        _assert(False, "invalid transition raises ValueError")
    except ValueError:
        _assert(True, "invalid transition raises ValueError")
    _assert(
        snapshot_of(RuntimeState.RUNNING, extra=1)["state"] == "running",
        "snapshot_of serializes state",
    )

    # --- sync task ---------------------------------------------------------------
    session = await engine.run("sync-task", _sync_task, 21)
    _assert(session.state == RuntimeState.SUCCEEDED, "sync task succeeds")
    _assert(session.result == 42, "sync task result propagated")
    _assert(session.started_at is not None and session.finished_at is not None, "session timestamps set")
    _assert(session.snapshot()["has_result"] is True, "session snapshot flags result")

    # --- async task ------------------------------------------------------------
    session = await engine.run("async-task", _async_task, 1)
    _assert(session.state == RuntimeState.SUCCEEDED, "async task succeeds")
    _assert(session.result == 2, "async task result propagated")

    # --- failing task ----------------------------------------------------------
    session = await engine.run("failing-task", _failing_task)
    _assert(session.state == RuntimeState.FAILED, "failing task settles to failed")
    _assert("boom" in (session.error or ""), "failure message recorded")
    _assert(session.snapshot()["has_result"] is False, "failed session has no result")

    # --- cancel path (manual transition) ------------------------------------------
    manual = engine.create_session("manual-cancel")
    await manual.cancel()
    _assert(manual.state == RuntimeState.CANCELLED, "manual cancel works")

    # --- cleanup ---------------------------------------------------------------
    cleaned: list[str] = []
    engine.cleanup.register(manual.id, lambda: cleaned.append(manual.id))
    _assert(engine.cleanup.snapshot()["pending_callbacks"] == 1, "cleanup callback registered")
    result = engine.close(manual.id)
    _assert(result["closed"] is True, "engine closes session")
    _assert(cleaned == [manual.id], "cleanup callback ran on close")
    _assert(engine.cleanup.snapshot()["pending_callbacks"] == 0, "cleanup drained after close")
    _assert(engine.get(manual.id) is None, "closed session removed from registry")

    # --- engine snapshot + metrics ------------------------------------------------
    snap = engine.snapshot()
    _assert(snap["counts"]["total"] >= 3, "engine tracks sessions")
    metrics = engine.metrics.snapshot()
    _assert(metrics["sessions"]["succeeded"] >= 2, "runtime metrics count succeeded")
    _assert(metrics["sessions"]["failed"] >= 1, "runtime metrics count failed")
    _assert(metrics["duration"]["count"] >= 3, "runtime metrics record durations")

    print("\nSMOKE OK — AIOS Runtime Engine")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
