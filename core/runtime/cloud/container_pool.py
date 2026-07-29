from __future__ import annotations

import asyncio
import uuid
from datetime import datetime
from typing import Any


class ContainerPool:
    def __init__(self, min_size: int = 3, max_size: int = 20):
        self.min_size = min_size
        self.max_size = max_size
        self._pool: dict[str, dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def start(self):
        for _ in range(self.min_size):
            await self._add_container()

    async def acquire(self, image: str = "superdev/agent-runner:latest") -> dict[str, Any] | None:
        async with self._lock:
            available = [c for c in self._pool.values() if c["status"] == "idle" and c["image"] == image]
            if available:
                container = available[0]
                container["status"] = "busy"
                container["acquired_at"] = datetime.utcnow().isoformat()
                return container
            if len(self._pool) < self.max_size:
                container = await self._add_container(image)
                container["status"] = "busy"
                container["acquired_at"] = datetime.utcnow().isoformat()
                return container
            return None

    async def release(self, container_id: str) -> bool:
        async with self._lock:
            container = self._pool.get(container_id)
            if not container:
                return False
            container["status"] = "idle"
            container["acquired_at"] = None
            container["usage_count"] = container.get("usage_count", 0) + 1
            return True

    async def _add_container(self, image: str = "superdev/agent-runner:latest") -> dict[str, Any]:
        cid = f"ctn_{uuid.uuid4().hex[:12]}"
        container = {
            "id": cid,
            "image": image,
            "status": "idle",
            "port": 9000 + hash(cid) % 1000,
            "created_at": datetime.utcnow().isoformat(),
            "usage_count": 0,
            "acquired_at": None,
        }
        self._pool[cid] = container
        return container

    async def scale_up(self, count: int = 3) -> int:
        added = 0
        async with self._lock:
            while len(self._pool) < min(self.max_size, len(self._pool) + count):
                await self._add_container()
                added += 1
        return added

    async def scale_down(self, count: int = 3) -> int:
        removed = 0
        async with self._lock:
            idle = [c for c in self._pool.values() if c["status"] == "idle"]
            for container in idle[:count]:
                self._pool.pop(container["id"], None)
                removed += 1
        return removed

    async def get_stats(self) -> dict[str, Any]:
        total = len(self._pool)
        busy = sum(1 for c in self._pool.values() if c["status"] == "busy")
        idle = total - busy
        return {"total": total, "busy": busy, "idle": idle, "min": self.min_size, "max": self.max_size}

    async def health_check(self) -> list[dict[str, Any]]:
        unhealthy = []
        async with self._lock:
            for cid, container in list(self._pool.items()):
                if container.get("usage_count", 0) > 100:
                    unhealthy.append(container)
                    self._pool.pop(cid, None)
                    await self._add_container(container["image"])
        return unhealthy

    async def shutdown(self):
        self._pool.clear()