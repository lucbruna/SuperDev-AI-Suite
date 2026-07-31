"""Network monitoring."""
from __future__ import annotations

import time
import uuid
from enum import Enum
from typing import Any


class ConnectionStatus(Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    BLOCKED = "blocked"
    SUSPICIOUS = "suspicious"

class NetworkConnection:
    def __init__(self, conn_id: str, source_ip: str, dest_ip: str, dest_port: int) -> None:
        self.conn_id = conn_id
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.status = ConnectionStatus.ACTIVE
        self.started_at = time.time()
        self.bytes_sent = 0
        self.bytes_received = 0

class NetworkMonitor:
    def __init__(self) -> None:
        self._connections: dict[str, NetworkConnection] = {}
        self._traffic_log: list[dict[str, Any]] = []
        self._suspicious_ports: set[int] = {22, 3389, 4444, 5555}
    def track_connection(self, source_ip: str, dest_ip: str, dest_port: int) -> NetworkConnection:
        conn_id = str(uuid.uuid4())[:8]
        conn = NetworkConnection(conn_id, source_ip, dest_ip, dest_port)
        if dest_port in self._suspicious_ports:
            conn.status = ConnectionStatus.SUSPICIOUS
        self._connections[conn_id] = conn
        return conn
    def update_traffic(self, conn_id: str, bytes_sent: int = 0, bytes_received: int = 0) -> bool:
        conn = self._connections.get(conn_id)
        if conn:
            conn.bytes_sent += bytes_sent
            conn.bytes_received += bytes_received
            self._traffic_log.append({"conn_id": conn_id, "bytes_sent": bytes_sent, "bytes_received": bytes_received, "timestamp": time.time()})
            return True
        return False
    def close_connection(self, conn_id: str) -> bool:
        conn = self._connections.get(conn_id)
        if conn:
            conn.status = ConnectionStatus.CLOSED
            return True
        return False
    def block_connection(self, conn_id: str) -> bool:
        conn = self._connections.get(conn_id)
        if conn:
            conn.status = ConnectionStatus.BLOCKED
            return True
        return False
    def get_active_connections(self) -> list[dict[str, Any]]:
        return [{"id": c.conn_id, "src": c.source_ip, "dst": c.dest_ip, "port": c.dest_port, "status": c.status.value} for c in self._connections.values() if c.status == ConnectionStatus.ACTIVE]
    def get_suspicious_connections(self) -> list[dict[str, Any]]:
        return [{"id": c.conn_id, "src": c.source_ip, "dst": c.dest_ip, "port": c.dest_port} for c in self._connections.values() if c.status == ConnectionStatus.SUSPICIOUS]
    def get_traffic_summary(self) -> dict[str, int]:
        total_sent = sum(c.bytes_sent for c in self._connections.values())
        total_received = sum(c.bytes_received for c in self._connections.values())
        return {"total_sent": total_sent, "total_received": total_received, "connections": len(self._connections)}
