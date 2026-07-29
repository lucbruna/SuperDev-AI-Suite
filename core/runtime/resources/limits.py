from __future__ import annotations

import os
import platform
import signal

from runtime_engine.sandbox.sandbox_limits import SandboxLimits


class ResourceLimits:
    def __init__(self) -> None:
        self._is_windows = platform.system() == "Windows"

    async def apply(self, pid: int, limits: SandboxLimits) -> bool:
        if self._is_windows:
            return await self._apply_windows(pid, limits)
        return await self._apply_unix(pid, limits)

    async def _apply_unix(self, pid: int, limits: SandboxLimits) -> bool:
        try:
            import resource
            if limits.max_time > 0:
                resource.setrlimit(resource.RLIMIT_CPU, (limits.max_time, limits.max_time + 5))
            if limits.max_memory > 0:
                mem_bytes = limits.max_memory * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
            if limits.max_processes > 0:
                resource.setrlimit(resource.RLIMIT_NPROC, (limits.max_processes, limits.max_processes))
            if limits.max_disk > 0:
                disk_bytes = limits.max_disk * 1024 * 1024
                resource.setrlimit(resource.RLIMIT_FSIZE, (disk_bytes, disk_bytes))
            return True
        except (ImportError, AttributeError, resource.error):
            return False

    async def _apply_windows(self, pid: int, limits: SandboxLimits) -> bool:
        try:
            import ctypes
            from ctypes import wintypes
            kernel32 = ctypes.windll.kernel32
            job = kernel32.CreateJobObjectW(None, None)
            class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
                _fields_ = [
                    ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
                    ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
                    ("LimitFlags", wintypes.DWORD),
                    ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t),
                    ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t),
                    ("ChildProcessBreak", wintypes.DWORD),
                    ("MaxProcessMemory", ctypes.c_size_t),
                    ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t),
                ]
            info = JOBOBJECT_BASIC_LIMIT_INFORMATION()
            flags = 0
            if limits.max_memory > 0:
                info.ProcessMemoryLimit = limits.max_memory * 1024 * 1024
                flags |= 0x200
            if limits.max_time > 0:
                info.PerProcessUserTimeLimit = wintypes.LARGE_INTEGER(limits.max_time * 10000000)
                flags |= 0x80
            info.LimitFlags = wintypes.DWORD(flags)
            kernel32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))
            kernel32.AssignProcessToJobObject(job, kernel32.OpenProcess(0x1F0FFF, False, pid))
            return True
        except (ImportError, AttributeError, Exception):
            return False
