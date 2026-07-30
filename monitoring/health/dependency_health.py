from __future__ import annotations

from typing import Any

from ..monitoring_models import HealthCheckResult, HealthStatus


class DependencyHealth:
    """Health checks for external dependencies."""

    @staticmethod
    def from_bool(component: str, is_healthy: bool, message: str = "") -> HealthCheckResult:
        return HealthCheckResult(
            component=component,
            status=HealthStatus.HEALTHY if is_healthy else HealthStatus.UNHEALTHY,
            message=message or ("OK" if is_healthy else "Unhealthy"),
        )

    @staticmethod
    def database(host: str, port: int, timeout: float = 3.0) -> HealthCheckResult:
        import socket
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            return HealthCheckResult(
                component=f"database_{host}:{port}",
                status=HealthStatus.HEALTHY,
                message=f"Database reachable at {host}:{port}",
            )
        except Exception as e:
            return HealthCheckResult(
                component=f"database_{host}:{port}",
                status=HealthStatus.UNHEALTHY,
                message=f"Database unreachable: {e}",
            )

    @staticmethod
    def cache(host: str, port: int, timeout: float = 2.0) -> HealthCheckResult:
        import socket
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            sock.close()
            return HealthCheckResult(
                component=f"cache_{host}:{port}",
                status=HealthStatus.HEALTHY,
                message=f"Cache reachable at {host}:{port}",
            )
        except Exception as e:
            return HealthCheckResult(
                component=f"cache_{host}:{port}",
                status=HealthStatus.UNHEALTHY,
                message=f"Cache unreachable: {e}",
            )

    @staticmethod
    def http_endpoint(url: str, timeout: float = 5.0) -> HealthCheckResult:
        import urllib.request
        try:
            req = urllib.request.Request(url, method="HEAD")
            resp = urllib.request.urlopen(req, timeout=timeout)
            return HealthCheckResult(
                component=f"http_{url}",
                status=HealthStatus.HEALTHY if resp.status < 500 else HealthStatus.DEGRADED,
                message=f"HTTP {resp.status} from {url}",
                dependencies={"status": resp.status},
            )
        except Exception as e:
            return HealthCheckResult(
                component=f"http_{url}",
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot reach {url}: {e}",
            )
