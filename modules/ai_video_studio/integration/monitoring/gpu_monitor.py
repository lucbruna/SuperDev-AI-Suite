"""GPU Monitor — probes nvidia-smi when present (offline stub otherwise)."""
from __future__ import annotations

import shutil
import subprocess
from typing import Any


class GPUMonitor:
    """Reports GPU availability, model and utilization."""

    def collect(self) -> dict[str, Any]:
        if shutil.which("nvidia-smi") is None:
            return {"available": False, "gpus": 0, "note": "no nvidia-smi on PATH"}
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10,
            )
            rows = [r for r in result.stdout.strip().splitlines() if r]
            return {
                "available": True,
                "gpus": len(rows),
                "devices": [
                    {"name": parts[0], "utilization_pct": int(parts[1]), "memory_mb": int(parts[2])}
                    for parts in (r.split(",") for r in rows) if len(parts) == 3
                ],
            }
        except Exception as e:  # noqa: BLE001
            return {"available": False, "gpus": 0, "error": str(e)}


_gpu_monitor: GPUMonitor | None = None


def get_gpu_monitor() -> GPUMonitor:
    global _gpu_monitor
    if _gpu_monitor is None:
        _gpu_monitor = GPUMonitor()
    return _gpu_monitor
