"""Sistema de health checks detalhados para o SuperDev."""

from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime
from typing import Any

import psutil


class HealthCheck:
    """Resultado de um health check individual."""

    def __init__(self, name: str, status: str, message: str = "", details: dict[str, Any] | None = None) -> None:
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.checked_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "checked_at": self.checked_at,
        }


class HealthMonitor:
    """Sistema de health checks para todos os componentes."""

    def __init__(self) -> None:
        self._checks: dict[str, Any] = {}
        self._start_time = time.time()

    def register_check(self, name: str, check_func: Any) -> None:
        self._checks[name] = check_func

    async def run_all_checks(self) -> dict[str, Any]:
        results: list[HealthCheck] = []
        overall_status = "healthy"

        for name, check_func in self._checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                results.append(result)
                if result.status == "unhealthy":
                    overall_status = "unhealthy"
                elif result.status == "degraded" and overall_status != "unhealthy":
                    overall_status = "degraded"
            except Exception as e:
                results.append(HealthCheck(name=name, status="unhealthy", message=str(e)))
                overall_status = "unhealthy"

        return {
            "status": overall_status,
            "timestamp": datetime.now(UTC).isoformat(),
            "uptime_seconds": time.time() - self._start_time,
            "checks": [r.to_dict() for r in results],
        }


def check_system() -> HealthCheck:
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    details = {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "disk_percent": disk.percent,
    }
    if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
        status = "unhealthy"
    elif cpu_percent > 70 or memory.percent > 70 or disk.percent > 80:
        status = "degraded"
    else:
        status = "healthy"
    return HealthCheck(name="system", status=status, message="Recursos do sistema", details=details)


def check_disk_space() -> HealthCheck:
    disk = psutil.disk_usage("/")
    details = {"total_gb": disk.total // (1024**3), "used_gb": disk.used // (1024**3), "percent": disk.percent}
    if disk.percent > 95:
        status = "unhealthy"
    elif disk.percent > 85:
        status = "degraded"
    else:
        status = "healthy"
    return HealthCheck(name="disk", status=status, message="Espaço em disco", details=details)


def check_memory() -> HealthCheck:
    memory = psutil.virtual_memory()
    details = {"total_mb": memory.total // (1024**2), "percent": memory.percent}
    if memory.percent > 95:
        status = "unhealthy"
    elif memory.percent > 80:
        status = "degraded"
    else:
        status = "healthy"
    return HealthCheck(name="memory", status=status, message="Memória", details=details)


health_monitor = HealthMonitor()
health_monitor.register_check("system", check_system)
health_monitor.register_check("disk", check_disk_space)
health_monitor.register_check("memory", check_memory)
