"""
Endpoint Detection and Response
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ThreatCategory(Enum):
    MALWARE = "malware"
    RANSOMWARE = "ransomware"
    ROOTKIT = "rootkit"
    TROJAN = "trojan"
    SPYWARE = "spyware"
    ADWARE = "adware"


@dataclass
class ProcessInfo:
    pid: int
    name: str
    path: str
    parent_pid: int = 0
    command_line: str = ""
    hash_sha256: str = ""
    is_suspicious: bool = False


@dataclass
class FileIntegrityEvent:
    event_id: str
    file_path: str
    event_type: str
    old_hash: str = ""
    new_hash: str = ""
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class EndpointAlert:
    alert_id: str
    endpoint_id: str
    threat_category: ThreatCategory
    severity: str = "medium"
    process: ProcessInfo | None = None
    message: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


class EndpointDefense:
    def __init__(self):
        self.processes: dict[int, ProcessInfo] = {}
        self.file_events: list[FileIntegrityEvent] = []
        self.alerts: list[EndpointAlert] = []
        self.blocked_hashes: set = set()
        self.monitored_paths: list[str] = []

    def monitor_process(self, pid: int, name: str, path: str, command_line: str = "") -> ProcessInfo:
        file_hash = hashlib.sha256(f"{name}{path}".encode()).hexdigest()
        is_suspicious = file_hash in self.blocked_hashes
        proc = ProcessInfo(
            pid=pid, name=name, path=path, command_line=command_line, hash_sha256=file_hash, is_suspicious=is_suspicious
        )
        self.processes[pid] = proc
        if is_suspicious:
            alert = EndpointAlert(
                alert_id=hashlib.sha256(f"alert_{pid}".encode()).hexdigest()[:16],
                endpoint_id="local",
                threat_category=ThreatCategory.MALWARE,
                process=proc,
                message=f"Suspicious process: {name}",
            )
            self.alerts.append(alert)
        return proc

    def record_file_event(
        self, file_path: str, event_type: str, old_hash: str = "", new_hash: str = ""
    ) -> FileIntegrityEvent:
        event = FileIntegrityEvent(
            event_id=hashlib.sha256(f"{file_path}{event_type}".encode()).hexdigest()[:16],
            file_path=file_path,
            event_type=event_type,
            old_hash=old_hash,
            new_hash=new_hash,
        )
        self.file_events.append(event)
        return event

    def block_hash(self, file_hash: str) -> None:
        self.blocked_hashes.add(file_hash)

    def add_monitored_path(self, path: str) -> None:
        self.monitored_paths.append(path)

    def get_alerts(self, threat_category: ThreatCategory = None) -> list[EndpointAlert]:
        if threat_category:
            return [a for a in self.alerts if a.threat_category == threat_category]
        return self.alerts

    def get_suspicious_processes(self) -> list[ProcessInfo]:
        return [p for p in self.processes.values() if p.is_suspicious]

    def get_file_events(self, file_path: str = None) -> list[FileIntegrityEvent]:
        if file_path:
            return [e for e in self.file_events if e.file_path == file_path]
        return self.file_events

    def count(self) -> int:
        return len(self.processes)
