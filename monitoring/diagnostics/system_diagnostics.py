from __future__ import annotations

import os
import platform
import time
from typing import Any

from .diagnostic_engine import DiagnosticResult


class SystemDiagnostics:
    """System-level diagnostic checks."""

    @staticmethod
    def check_disk_space(path: str = "/") -> DiagnosticResult:
        try:
            free_gb = 0.0
            total_gb = 0.0
            pct = 0.0
            statvfs_func = getattr(os, "statvfs", None)
            if statvfs_func is not None:
                usage = statvfs_func(path)
                free_gb = (usage.f_bavail * usage.f_frsize) / (1024 ** 3)
                total_gb = (usage.f_blocks * usage.f_frsize) / (1024 ** 3)
                pct = ((total_gb - free_gb) / total_gb) * 100
            else:
                import shutil
                usage = shutil.disk_usage(path)
                free_gb = usage.free / (1024 ** 3)
                total_gb = usage.total / (1024 ** 3)
                pct = (usage.used / usage.total) * 100

            status = "passed"
            message = f"Disk space: {free_gb:.1f}GB free / {total_gb:.1f}GB total"
            if pct > 90:
                status = "failed"
                message = f"Critical: disk {pct:.0f}% full"
            elif pct > 75:
                status = "warning"
                message = f"Warning: disk {pct:.0f}% full"

            return DiagnosticResult(
                check="disk_space",
                status=status,
                message=message,
                details={"free_gb": round(free_gb, 1), "total_gb": round(total_gb, 1), "usage_pct": round(pct, 1)},
            )
        except Exception as e:
            return DiagnosticResult(check="disk_space", status="error", message=str(e))

    @staticmethod
    def check_memory() -> DiagnosticResult:
        try:
            import psutil
            mem = psutil.virtual_memory()
            status = "passed"
            message = f"Memory: {mem.percent}% used"
            if mem.percent > 90:
                status = "failed"
            elif mem.percent > 75:
                status = "warning"
            return DiagnosticResult(
                check="memory",
                status=status,
                message=message,
                details={
                    "total_mb": round(mem.total / (1024**2), 1),
                    "available_mb": round(mem.available / (1024**2), 1),
                    "percent": mem.percent,
                },
            )
        except ImportError:
            return DiagnosticResult(check="memory", status="warning", message="psutil not available")

    @staticmethod
    def check_cpu_load() -> DiagnosticResult:
        try:
            import psutil
            load = psutil.cpu_percent(interval=0.5)
            status = "passed"
            message = f"CPU load: {load}%"
            if load > 90:
                status = "failed"
            elif load > 70:
                status = "warning"
            return DiagnosticResult(
                check="cpu_load",
                status=status,
                message=message,
                details={"cpu_percent": load, "cpu_count": os.cpu_count() or 0},
            )
        except ImportError:
            return DiagnosticResult(check="cpu_load", status="warning", message="psutil not available")

    @staticmethod
    def check_platform() -> DiagnosticResult:
        return DiagnosticResult(
            check="platform",
            status="passed",
            message=f"Platform: {platform.system()} {platform.release()}",
            details={
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "python": platform.python_version(),
            },
        )
