from __future__ import annotations

import socket
from typing import Any

from .diagnostic_engine import DiagnosticResult


class NetworkDiagnostics:
    """Network connectivity and health diagnostic checks."""

    @staticmethod
    def check_dns(hostname: str = "google.com") -> DiagnosticResult:
        try:
            addr = socket.getaddrinfo(hostname, 80)
            ips = list({str(a[4][0]) for a in addr})
            return DiagnosticResult(
                check="dns_resolution",
                status="passed",
                message=f"DNS resolved {hostname} -> {', '.join(ips[:3])}",
                details={"hostname": hostname, "ips": ips[:5]},
            )
        except Exception as e:
            return DiagnosticResult(
                check="dns_resolution",
                status="failed",
                message=f"DNS resolution failed for {hostname}: {e}",
            )

    @staticmethod
    def check_port(host: str = "localhost", port: int = 80, timeout: float = 3.0) -> DiagnosticResult:
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            return DiagnosticResult(
                check=f"port_{port}",
                status="passed",
                message=f"Port {port} on {host} is open",
                details={"host": host, "port": port},
            )
        except Exception as e:
            return DiagnosticResult(
                check=f"port_{port}",
                status="failed",
                message=f"Port {port} on {host} unreachable: {e}",
                details={"host": host, "port": port, "error": str(e)},
            )

    @staticmethod
    def check_localhost() -> DiagnosticResult:
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return DiagnosticResult(
                check="localhost",
                status="passed",
                message=f"Hostname: {hostname}, IP: {local_ip}",
                details={"hostname": hostname, "local_ip": local_ip},
            )
        except Exception as e:
            return DiagnosticResult(check="localhost", status="error", message=str(e))
