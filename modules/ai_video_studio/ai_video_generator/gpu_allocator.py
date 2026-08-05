"""GPU allocator — manage GPU memory and device assignment."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.core.exceptions import GPUError


class GPUAllocator:
    """Tracks GPU memory usage and allocates requests to devices."""

    def __init__(self) -> None:
        # device_id -> total/used MB
        self._devices: dict[int, dict[str, Any]] = {
            0: {"total_mb": 24000, "used_mb": 0},
        }

    def register_device(self, device_id: int, total_mb: int) -> None:
        self._devices[device_id] = {"total_mb": total_mb, "used_mb": 0}

    def allocate(self, required_mb: int) -> int:
        """Reserve memory on the least-loaded device; raises GPUError if none."""
        best: tuple[int, dict[str, Any]] | None = None
        for device_id, info in self._devices.items():
            if info["total_mb"] - info["used_mb"] >= required_mb:
                if best is None or info["used_mb"] < best[1]["used_mb"]:
                    best = (device_id, info)
        if best is None:
            raise GPUError(f"No GPU with {required_mb}MB free")
        device_id, info = best
        info["used_mb"] += required_mb
        return device_id

    def release(self, device_id: int, required_mb: int) -> None:
        info = self._devices.get(device_id)
        if info is not None:
            info["used_mb"] = max(0, info["used_mb"] - required_mb)

    def available_mb(self, device_id: int | None = None) -> int:
        if device_id is not None:
            info = self._devices.get(device_id)
            return (info["total_mb"] - info["used_mb"]) if info else 0
        return sum(i["total_mb"] - i["used_mb"] for i in self._devices.values())

    def snapshot(self) -> list[dict[str, Any]]:
        return [
            {"device_id": device_id, **info}
            for device_id, info in self._devices.items()
        ]


_gpu_allocator: GPUAllocator | None = None


def get_gpu_allocator() -> GPUAllocator:
    global _gpu_allocator
    if _gpu_allocator is None:
        _gpu_allocator = GPUAllocator()
    return _gpu_allocator
