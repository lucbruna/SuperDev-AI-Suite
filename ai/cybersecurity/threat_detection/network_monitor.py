"""
Network Traffic Monitoring
"""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Protocol(Enum):
    TCP = "tcp"
    UDP = "udp"
    HTTP = "http"
    HTTPS = "https"
    DNS = "dns"
    SSH = "ssh"
    UNKNOWN = "unknown"


@dataclass
class NetworkFlow:
    flow_id: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: Protocol = Protocol.TCP
    bytes_sent: int = 0
    bytes_received: int = 0
    packets: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    duration_seconds: float = 0.0


@dataclass
class TrafficAnomaly:
    anomaly_id: str
    flow_id: str
    anomaly_type: str
    description: str = ""
    severity: str = "medium"
    detected_at: datetime = field(default_factory=datetime.now)


class NetworkMonitor:
    def __init__(self):
        self.flows: dict[str, NetworkFlow] = {}
        self.anomalies: list[TrafficAnomaly] = []
        self.baseline: dict[str, float] = {}
        self.blocked_connections: set = set()

    def record_flow(self, src_ip: str, dst_ip: str, src_port: int, dst_port: int, protocol: Protocol = Protocol.TCP, bytes_sent: int = 0, bytes_received: int = 0) -> NetworkFlow:
        flow_id = hashlib.sha256(f"{src_ip}:{dst_ip}:{src_port}:{dst_port}".encode()).hexdigest()[:16]
        flow = NetworkFlow(flow_id=flow_id, src_ip=src_ip, dst_ip=dst_ip, src_port=src_port, dst_port=dst_port, protocol=protocol, bytes_sent=bytes_sent, bytes_received=bytes_received)
        self.flows[flow_id] = flow
        return flow

    def detect_anomaly(self, flow: NetworkFlow) -> TrafficAnomaly | None:
        avg_bytes = self.baseline.get("avg_bytes", 1000)
        if flow.bytes_sent > avg_bytes * 10:
            anomaly = TrafficAnomaly(anomaly_id=hashlib.sha256(flow.flow_id.encode()).hexdigest()[:16], flow_id=flow.flow_id, anomaly_type="high_volume", description=f"Bytes sent: {flow.bytes_sent}", severity="high")
            self.anomalies.append(anomaly)
            return anomaly
        return None

    def block_connection(self, src_ip: str, dst_ip: str) -> None:
        self.blocked_connections.add(f"{src_ip}:{dst_ip}")

    def is_blocked(self, src_ip: str, dst_ip: str) -> bool:
        return f"{src_ip}:{dst_ip}" in self.blocked_connections

    def update_baseline(self, metric: str, value: float) -> None:
        self.baseline[metric] = value

    def get_flows_by_ip(self, ip: str) -> list[NetworkFlow]:
        return [f for f in self.flows.values() if f.src_ip == ip or f.dst_ip == ip]

    def get_flows_by_protocol(self, protocol: Protocol) -> list[NetworkFlow]:
        return [f for f in self.flows.values() if f.protocol == protocol]

    def get_anomalies(self) -> list[TrafficAnomaly]:
        return self.anomalies

    def count(self) -> int:
        return len(self.flows)
