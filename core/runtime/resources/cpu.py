from __future__ import annotations

import asyncio
import os
import platform
from typing import Sequence

from pydantic import BaseModel, Field


class CPUInfo(BaseModel):
    total_cores: int
    available_cores: int
    usage_percent: float
    frequency_mhz: float = 0.0


class CPUManager:
    def __init__(self) -> None:
        self._is_windows = platform.system() == "Windows"

    def get_available_cores(self) -> int:
        if self._is_windows:
            count = os.cpu_count() or 1
            try:
                import psutil
                return psutil.cpu_count(logical=True) or count
            except ImportError:
                return count
        return len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else (os.cpu_count() or 1)

    def get_usage(self) -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except ImportError:
            return 0.0

    def get_info(self) -> CPUInfo:
        try:
            import psutil
            return CPUInfo(
                total_cores=psutil.cpu_count(logical=True) or 1,
                available_cores=psutil.cpu_count(logical=True) or 1,
                usage_percent=psutil.cpu_percent(interval=0.1),
                frequency_mhz=psutil.cpu_freq().current if psutil.cpu_freq() else 0.0,
            )
        except ImportError:
            return CPUInfo(
                total_cores=os.cpu_count() or 1,
                available_cores=os.cpu_count() or 1,
                usage_percent=0.0,
            )

    def set_affinity(self, pid: int, cores: list[int]) -> bool:
        try:
            import psutil
            proc = psutil.Process(pid)
            proc.cpu_affinity(cores)
            return True
        except (ImportError, psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    async def limit(self, pid: int, max_cores: float) -> bool:
        if self._is_windows:
            return False
        try:
            import psutil
            proc = psutil.Process(pid)
            total = psutil.cpu_count(logical=True) or 1
            if max_cores < total:
                core_count = max(1, int(max_cores))
                proc.cpu_affinity(list(range(core_count)))
            return True
        except (ImportError, psutil.NoSuchProcess, psutil.AccessDenied):
            return False
