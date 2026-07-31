"""Compute instance provisioning (Volume 37, Fase 2)."""

from __future__ import annotations

import random

from devops_engine.devops_models import (CloudProvider, ResourceStatus,
                                         Server)
from devops_engine.devops_protocols import new_id, now


class InstanceManager:
    """Provisions and terminates compute servers."""

    def __init__(self) -> None:
        self._servers: dict[str, Server] = {}

    def provision(self, name: str, cpu: int = 2, memory_gb: int = 4,
                  provider: CloudProvider | None = None,
                  region: str | None = None) -> Server:
        server = Server(
            server_id=new_id("server"),
            name=name,
            provider=provider or CloudProvider.AWS,
            region=region or "us-east-1",
            cpu=cpu,
            memory_gb=memory_gb,
            status=ResourceStatus.RUNNING,
            ip_address=f"10.0.{random.randint(0, 255)}"
                       f".{random.randint(1, 254)}",
            created_at=now(),
        )
        self._servers[server.server_id] = server
        return server

    def terminate(self, server_id: str) -> bool:
        server = self._servers.get(server_id)
        if server is None:
            return False
        server.status = ResourceStatus.TERMINATED
        return True

    def get(self, server_id: str) -> Server | None:
        return self._servers.get(server_id)

    def list(self) -> list[Server]:
        return list(self._servers.values())

    def count(self) -> int:
        return len(self._servers)
