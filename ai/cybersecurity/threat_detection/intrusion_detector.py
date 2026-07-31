"""
Intrusion Detection System
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class AlertSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class DetectionSignature:
    signature_id: str
    name: str
    pattern: str
    severity: AlertSeverity = AlertSeverity.MEDIUM
    enabled: bool = True
    description: str = ""


@dataclass
class Alert:
    alert_id: str
    signature_id: str
    source_ip: str = ""
    dest_ip: str = ""
    message: str = ""
    severity: AlertSeverity = AlertSeverity.MEDIUM
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntrusionDetector:
    def __init__(self):
        self.signatures: Dict[str, DetectionSignature] = {}
        self.alerts: List[Alert] = []
        self.blocked_ips: set = set()
        self.threshold: int = 10

    def add_signature(self, name: str, pattern: str, severity: AlertSeverity = AlertSeverity.MEDIUM) -> DetectionSignature:
        sig_id = hashlib.sha256(pattern.encode()).hexdigest()[:16]
        sig = DetectionSignature(signature_id=sig_id, name=name, pattern=pattern, severity=severity)
        self.signatures[sig_id] = sig
        return sig

    def analyze_packet(self, source_ip: str, payload: str) -> Optional[Alert]:
        for sig in self.signatures.values():
            if not sig.enabled:
                continue
            if sig.pattern.lower() in payload.lower():
                alert = Alert(alert_id=hashlib.sha256(f"{source_ip}{payload}".encode()).hexdigest()[:16], signature_id=sig.signature_id, source_ip=source_ip, message=f"Detected: {sig.name}", severity=sig.severity)
                self.alerts.append(alert)
                return alert
        return None

    def block_ip(self, ip: str) -> None:
        self.blocked_ips.add(ip)

    def is_blocked(self, ip: str) -> bool:
        return ip in self.blocked_ips

    def get_alerts(self, severity: AlertSeverity = None) -> List[Alert]:
        if severity:
            return [a for a in self.alerts if a.severity == severity]
        return self.alerts

    def get_alerts_by_ip(self, ip: str) -> List[Alert]:
        return [a for a in self.alerts if a.source_ip == ip]

    def disable_signature(self, sig_id: str) -> bool:
        sig = self.signatures.get(sig_id)
        if sig:
            sig.enabled = False
            return True
        return False

    def count(self) -> int:
        return len(self.alerts)
