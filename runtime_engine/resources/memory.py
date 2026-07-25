from __future__ import annotations

import os
import platform
import asyncio
from typing import Any

from pydantic import BaseModel, Field


class MemoryInfo(BaseModel):
    total_mb: float
    available_mb: float
    used_mb: float
    usage_percent: float


class MemoryManager:
    def __init__(self) -> None:
        self._is_windows = platform.system() == "Windows"

    def get_available_memory(self) -> float:
        try:
            import psutil
            return psutil.virtual_memory().available / (1024 * 1024)
        except ImportError:
            return 0.0

    def get_usage(self) -> MemoryInfo:
        try:
            import psutil
            mem = psutil.virtual_memory()
            return MemoryInfo(
                total_mb=mem.total / (1024 * 1024),
                available_mb=mem.available / (1024 * 1024),
                used_mb=mem.used / (1024 * 1024),
                usage_percent=mem.percent,
            )
        except ImportError:
            return MemoryInfo(total_mb=0.0, available_mb=0.0, used_mb=0.0, usage_percent=0.0)

    def get_process_usage(self, pid: int) -> float:
        try:
            import psutil
            proc = psutil.Process(pid)
            return proc.memory_info().rss / (1024 * 1024)
        except (ImportError, psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0

    async def limit(self, pid: int, max_mb: int) -> bool:
        if self._is_windows:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            job = kernel32.CreateJobObjectW(None, None)
            from ctypes import wintypes
            class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
                _fields_ = [
                    ("BasicLimitInformation", wintypes.LARGE_INTEGER * 6),
                    ("IoInfo", wintypes.LARGE_INTEGER * 3),
                    ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t),
                    ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t),
                ]
            info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
            info.ProcessMemoryLimit = max_mb * 1024 * 1024
            kernel32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))
            kernel32.AssignProcessToJobObject(job, kernel32.OpenProcess(0x1F0FFF, False, pid))
            return True
        try:
            import resource
            limit_bytes = max_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, limit_bytes))
            return True
        except (ImportError, AttributeError, resource.error):
            return False
