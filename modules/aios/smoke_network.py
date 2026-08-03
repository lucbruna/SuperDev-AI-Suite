"""Smoke test for the AIOS network runtime (Volume 12, Fase 27).

Exercises ACL, real DNS resolution, local TCP port probing and a local HTTP
server so it does not depend on external network. Run from repo root:

    python modules/aios/smoke_network.py
"""
from __future__ import annotations

import asyncio
import http.server
import socket
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from modules.aios import (  # noqa: E402
    KernelPermissionDeniedError,
    NetworkRuntime,
    get_kernel_security,
    get_network_runtime,
)


def _assert(cond: bool, label: str) -> None:
    if not cond:
        raise AssertionError(f"FAIL: {label}")
    print(f"  ok - {label}")


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


async def main() -> int:
    runtime: NetworkRuntime = get_network_runtime()

    security = get_kernel_security()
    security.grant(
        "network",
        "proxy",
        "firewall",
        "dns",
        "ports",
        "http",
        "websocket",
        "grpc",
    )

    # --- ACL ----------------------------------------------------------------------
    security.revoke("network", "dns")
    try:
        runtime.dns.resolve("localhost")
        _assert(False, "ACL denies revoked dns action")
    except KernelPermissionDeniedError:
        _assert(True, "ACL denies revoked dns action")
    security.grant("network", "dns")

    # --- proxy --------------------------------------------------------------------
    res = runtime.proxy.get()
    _assert(res["ok"] and "config" in res, "proxy reports configuration")

    # --- firewall ----------------------------------------------------------------
    res = runtime.firewall.status()
    _assert(res["ok"] and "platform" in res, "firewall reports platform status")

    # --- dns ---------------------------------------------------------------------
    res = runtime.dns.resolve("localhost")
    _assert(res["ok"] and any("127.0.0.1" in a for a in res["addresses"]), "dns resolves localhost")

    # --- ports (local socket server) ----------------------------------------------
    port = _free_port()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", port))
    server.listen(1)
    try:
        res = runtime.ports.is_open("127.0.0.1", port)
        _assert(res["ok"] and res["open"] is True, "ports detects an open local port")
        res = runtime.ports.is_open("127.0.0.1", 1)
        _assert(res["ok"] and res["open"] is False, "ports reports a closed port")
    finally:
        server.close()

    # --- http (local HTTP server) -------------------------------------------------
    http_port = _free_port()
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", http_port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        res = runtime.http.head(f"http://127.0.0.1:{http_port}/")
        _assert(res["ok"] and res["status"] == 200, "http HEAD returns 200 on local server")
    finally:
        httpd.shutdown()
        httpd.server_close()

    # --- websocket / grpc (degrade gracefully) ------------------------------------
    res = runtime.websocket.check("ws://127.0.0.1:1")
    _assert(res["ok"], "websocket check returns a result")
    res = runtime.grpc.available()
    _assert(res["ok"] and "available" in res, "grpc reports availability")

    # --- snapshot ----------------------------------------------------------------
    snap = await runtime.snapshot()
    _assert("proxy" in snap and "dns" in snap and "ports" in snap, "snapshot exposes network inventory")

    print("\nSMOKE OK — AIOS Network")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
