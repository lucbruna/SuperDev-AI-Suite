from __future__ import annotations

import socket
import urllib.request
from typing import Any

from .diagnostic_engine import DiagnosticResult


class ConnectivityCheck:
    """Endpoint reachability and connectivity checks."""

    @staticmethod
    def check_http(url: str, timeout: float = 5.0) -> DiagnosticResult:
        try:
            req = urllib.request.Request(url, method="HEAD")
            resp = urllib.request.urlopen(req, timeout=timeout)
            return DiagnosticResult(
                check=f"http_{url}",
                status="passed",
                message=f"HTTP {resp.status} from {url}",
                details={"url": url, "status": resp.status, "ms": 0},
            )
        except Exception as e:
            return DiagnosticResult(
                check=f"http_{url}",
                status="failed",
                message=f"Cannot reach {url}: {e}",
                details={"url": url, "error": str(e)},
            )

    @staticmethod
    def check_tcp(host: str, port: int, timeout: float = 3.0) -> DiagnosticResult:
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            return DiagnosticResult(
                check=f"tcp_{host}:{port}",
                status="passed",
                message=f"TCP connection to {host}:{port} successful",
                details={"host": host, "port": port},
            )
        except Exception as e:
            return DiagnosticResult(
                check=f"tcp_{host}:{port}",
                status="failed",
                message=f"Cannot connect to {host}:{port}: {e}",
                details={"host": host, "port": port, "error": str(e)},
            )
