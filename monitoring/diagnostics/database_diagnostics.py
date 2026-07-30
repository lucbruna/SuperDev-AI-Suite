from __future__ import annotations

from typing import Any

from .diagnostic_engine import DiagnosticResult


class DatabaseDiagnostics:
    """Database connection and health diagnostic checks."""

    @staticmethod
    def check_connection(host: str = "localhost", port: int = 5432, timeout: float = 3.0) -> DiagnosticResult:
        import socket
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            return DiagnosticResult(
                check="database_connection",
                status="passed",
                message=f"Database at {host}:{port} reachable",
                details={"host": host, "port": port},
            )
        except Exception as e:
            return DiagnosticResult(
                check="database_connection",
                status="failed",
                message=f"Cannot connect to database at {host}:{port}: {e}",
            )

    @staticmethod
    def check_pool_config(
        min_size: int = 2,
        max_size: int = 20,
        current_size: int = 0,
    ) -> DiagnosticResult:
        issues: list[str] = []
        if min_size < 1:
            issues.append("min_size must be >= 1")
        if max_size < min_size:
            issues.append("max_size must be >= min_size")
        if current_size > max_size:
            issues.append("current_size exceeds max_size")

        if issues:
            return DiagnosticResult(
                check="database_pool",
                status="failed",
                message="; ".join(issues),
                details={"min_size": min_size, "max_size": max_size, "current_size": current_size},
            )
        return DiagnosticResult(
            check="database_pool",
            status="passed",
            message=f"Pool config valid (min={min_size}, max={max_size}, current={current_size})",
            details={"min_size": min_size, "max_size": max_size, "current_size": current_size},
        )

    @staticmethod
    def check_query_performance(avg_latency_ms: float, threshold_ms: float = 100.0) -> DiagnosticResult:
        status = "passed" if avg_latency_ms <= threshold_ms else "failed"
        return DiagnosticResult(
            check="query_performance",
            status=status,
            message=f"Avg latency: {avg_latency_ms:.1f}ms (threshold: {threshold_ms:.0f}ms)",
            details={"avg_latency_ms": avg_latency_ms, "threshold_ms": threshold_ms},
        )
