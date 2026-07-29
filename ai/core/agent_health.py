from __future__ import annotations

import time
from typing import Any


async def check_agent_health(agent_id: str) -> dict[str, Any]:
    memory_usage = _get_memory_usage()
    return {
        "agent_id": agent_id,
        "status": "unknown",
        "last_heartbeat": time.time(),
        "memory_usage": memory_usage,
        "error_count": 0,
        "healthy": memory_usage < 90.0,
        "checked_at": time.time(),
    }


def _get_memory_usage() -> float:
    try:
        import psutil
        return psutil.virtual_memory().percent
    except ImportError:
        try:
            import os
            if hasattr(os, "times"):
                return 0.0
        except Exception:
            pass
        return 0.0
