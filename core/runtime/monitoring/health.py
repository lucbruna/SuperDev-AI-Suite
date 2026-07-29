from __future__ import annotations

import shutil
from datetime import datetime

from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    healthy: bool
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    checks: dict[str, bool | str] = Field(default_factory=dict)


class RuntimeHealth:
    async def check(self) -> HealthStatus:
        checks: dict[str, bool | str] = {}

        checks["disk_space"] = await self._check_disk()
        checks["python"] = shutil.which("python3") is not None or shutil.which("python") is not None
        checks["node"] = shutil.which("node") is not None
        checks["docker"] = shutil.which("docker") is not None

        healthy = all(
            isinstance(v, bool) and v for v in checks.values()
        )
        return HealthStatus(healthy=healthy, checks=checks)

    async def _check_disk(self) -> bool:
        try:
            import psutil
            disk = psutil.disk_usage("/")
            return disk.free > 100 * 1024 * 1024
        except ImportError:
            return True

    async def check_docker_daemon(self) -> bool:
        docker_path = shutil.which("docker")
        if not docker_path:
            return False
        import asyncio
        proc = await asyncio.create_subprocess_exec(
            docker_path, "info",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        return proc.returncode == 0
