"""
Infrastructure Dashboard
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class ServerInfo:
    name: str
    status: str = "running"
    cpu: float = 0
    memory: float = 0
    disk: float = 0
    network_in: float = 0
    network_out: float = 0


class InfrastructureDashboard:
    def __init__(self):
        self.servers: list[ServerInfo] = []

    def add_server(self, server: ServerInfo) -> None:
        self.servers.append(server)

    def update_server(self, name: str, **kwargs) -> None:
        for s in self.servers:
            if s.name == name:
                for k, v in kwargs.items():
                    if hasattr(s, k):
                        setattr(s, k, v)
                return

    def get_overall_health(self) -> str:
        if not self.servers:
            return "unknown"
        unhealthy = [s for s in self.servers if s.status != "running"]
        if len(unhealthy) > len(self.servers) * 0.5:
            return "critical"
        if unhealthy:
            return "warning"
        return "healthy"

    def render(self) -> dict[str, Any]:
        return {
            "servers": [{"name": s.name, "status": s.status, "cpu": s.cpu, "memory": s.memory} for s in self.servers],
            "health": self.get_overall_health(),
            "totalServers": len(self.servers),
        }
