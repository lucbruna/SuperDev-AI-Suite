from __future__ import annotations

from typing import Any


class ResourceRequest:
    def __init__(self, cpu: float = 1.0, memory_mb: int = 256, priority: int = 0):
        self.cpu = cpu
        self.memory_mb = memory_mb
        self.priority = priority


class PlannerResourceAllocator:
    """Allocates resources for plan execution."""

    def __init__(self):
        self.max_cpu: float = 8.0
        self.max_memory_mb: int = 4096
        self._allocated_cpu: float = 0.0
        self._allocated_memory: int = 0

    def can_allocate(self, request: ResourceRequest) -> bool:
        return (
            self._allocated_cpu + request.cpu <= self.max_cpu
            and self._allocated_memory + request.memory_mb <= self.max_memory_mb
        )

    def allocate(self, request: ResourceRequest) -> bool:
        if not self.can_allocate(request):
            return False
        self._allocated_cpu += request.cpu
        self._allocated_memory += request.memory_mb
        return True

    def release(self, request: ResourceRequest) -> None:
        self._allocated_cpu = max(0.0, self._allocated_cpu - request.cpu)
        self._allocated_memory = max(0, self._allocated_memory - request.memory_mb)

    def usage(self) -> dict[str, Any]:
        return {
            "cpu_used": self._allocated_cpu,
            "cpu_max": self.max_cpu,
            "memory_mb_used": self._allocated_memory,
            "memory_mb_max": self.max_memory_mb,
            "cpu_percent": round((self._allocated_cpu / self.max_cpu) * 100, 1),
        }
