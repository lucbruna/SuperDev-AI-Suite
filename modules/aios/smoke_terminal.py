"""Smoke test for the AIOS terminal runtime (Volume 12, Fase 25).

Exercises ACL, tab/session management, a real command run through the host
shell (powershell.exe on Windows), history recording, builtin command
registry and output streaming. Run from repo root:

    python modules/aios/smoke_terminal.py
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KernelPermissionDeniedError,
    Terminal,
    TerminalSessionError,
    get_kernel_security,
    get_terminal_runtime,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


async def main() -> int:
    terminal: Terminal = get_terminal_runtime()

    security = get_kernel_security()
    security.grant("terminal", "run", "session")

    # --- ACL ----------------------------------------------------------------------
    security.revoke("terminal", "run")
    try:
        await terminal.run("echo hi")
        _assert(False, "ACL denies revoked run action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked run action")
    security.grant("terminal", "run")

    # --- tabs / sessions ------------------------------------------------------------
    opened = await terminal.open_tab("main")
    _assert(opened["tab"] == "main", "tab opens with a session")
    _assert(terminal.tabs.active == "main", "opened tab becomes active")
    try:
        await terminal.open_tab("main")
        _assert(False, "duplicate tab raises TerminalSessionError")
    except TerminalSessionError:
        _assert(True, "duplicate tab raises TerminalSessionError")

    # --- real command run ---------------------------------------------------------------
    result = await terminal.run("Write-Output 'hello terminal'")
    _assert(result["ok"] and "hello terminal" in result["stdout"], "terminal runs a command")

    # --- history --------------------------------------------------------------------------
    await terminal.run("Write-Output 'second'")
    history = terminal.history.list()
    _assert(len(history) == 2 and history[-1].startswith("Write-Output 'second'"), "history records commands")
    _assert(len(terminal.history.filter("second")) == 1, "history filters by term")

    # --- stream capture ---------------------------------------------------------------------
    _assert(any("hello terminal" in line for line in terminal.tabs.get("main").stream.lines()), "stream captures output")

    # --- builtin commands ----------------------------------------------------------------------
    names = terminal.commands.names()
    _assert("help" in names and "history" in names, "builtin commands are registered")

    # --- snapshot + close ---------------------------------------------------------------------
    snap = await terminal.snapshot()
    _assert(snap["tabs"] == ["main"] and snap["history_entries"] == 2, "snapshot reflects state")
    closed = await terminal.close_tab()
    _assert(closed.get("closed") == "main", "tab closes")
    _assert(terminal.tabs.list() == [], "tab list empties after close")

    print("\nSMOKE OK — AIOS Terminal")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
