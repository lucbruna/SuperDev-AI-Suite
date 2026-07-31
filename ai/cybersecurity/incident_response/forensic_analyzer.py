"""
Digital Forensics Analyzer
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class EvidenceType(Enum):
    LOG = "log"
    MEMORY_DUMP = "memory_dump"
    DISK_IMAGE = "disk_image"
    NETWORK_CAPTURE = "network_capture"
    REGISTRY = "registry"
    FILE_SYSTEM = "file_system"


@dataclass
class EvidenceItem:
    evidence_id: str
    evidence_type: EvidenceType
    source: str
    hash_sha256: str = ""
    collected_at: datetime = field(default_factory=datetime.now)
    chain_of_custody: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimelineEntry:
    timestamp: datetime
    event_type: str
    description: str = ""
    source: str = ""
    evidence_id: str = ""


class ForensicAnalyzer:
    def __init__(self):
        self.evidence: Dict[str, EvidenceItem] = {}
        self.timeline: List[TimelineEntry] = []

    def collect_evidence(self, evidence_type: EvidenceType, source: str, data: str = "", **kwargs) -> EvidenceItem:
        evidence_id = hashlib.sha256(f"{evidence_type.value}{source}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        data_hash = hashlib.sha256(data.encode()).hexdigest() if data else ""
        item = EvidenceItem(evidence_id=evidence_id, evidence_type=evidence_type, source=source, hash_sha256=data_hash, chain_of_custody=[{"action": "collected", "time": datetime.now().isoformat(), "by": "system"}])
        self.evidence[evidence_id] = item
        return item

    def transfer_custody(self, evidence_id: str, from_party: str, to_party: str) -> bool:
        item = self.evidence.get(evidence_id)
        if item:
            item.chain_of_custody.append({"action": "transfer", "from": from_party, "to": to_party, "time": datetime.now().isoformat()})
            return True
        return False

    def add_timeline_entry(self, timestamp: datetime, event_type: str, description: str = "", source: str = "") -> TimelineEntry:
        entry = TimelineEntry(timestamp=timestamp, event_type=event_type, description=description, source=source)
        self.timeline.append(entry)
        self.timeline.sort(key=lambda e: e.timestamp)
        return entry

    def get_timeline(self, start: datetime = None, end: datetime = None) -> List[TimelineEntry]:
        results = self.timeline
        if start:
            results = [e for e in results if e.timestamp >= start]
        if end:
            results = [e for e in results if e.timestamp <= end]
        return results

    def verify_evidence(self, evidence_id: str) -> bool:
        return evidence_id in self.evidence

    def get_evidence(self, evidence_id: str) -> Optional[EvidenceItem]:
        return self.evidence.get(evidence_id)

    def get_evidence_by_type(self, evidence_type: EvidenceType) -> List[EvidenceItem]:
        return [e for e in self.evidence.values() if e.evidence_type == evidence_type]

    def count(self) -> int:
        return len(self.evidence)
