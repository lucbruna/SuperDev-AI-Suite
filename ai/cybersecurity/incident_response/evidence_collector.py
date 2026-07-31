"""
Evidence Collection and Management
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class EvidenceFormat(Enum):
    RAW = "raw"
    JSON = "json"
    BINARY = "binary"
    LOG = "log"
    CAPTURE = "capture"


@dataclass
class CollectedEvidence:
    evidence_id: str
    name: str
    evidence_format: EvidenceFormat
    data_hash: str
    size_bytes: int = 0
    source: str = ""
    collector: str = ""
    collected_at: datetime = field(default_factory=datetime.now)
    storage_path: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    tamper_detected: bool = False


class EvidenceCollector:
    def __init__(self):
        self.evidence: Dict[str, CollectedEvidence] = {}
        self.storage_path: str = "/evidence/"
        self.hash_log: List[Dict[str, str]] = []

    def collect(self, name: str, data: str, evidence_format: EvidenceFormat = EvidenceFormat.RAW, source: str = "", collector: str = "") -> CollectedEvidence:
        evidence_id = hashlib.sha256(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        data_hash = hashlib.sha256(data.encode()).hexdigest()
        size_bytes = len(data.encode())
        evidence = CollectedEvidence(evidence_id=evidence_id, name=name, evidence_format=evidence_format, data_hash=data_hash, size_bytes=size_bytes, source=source, collector=collector, storage_path=f"{self.storage_path}{evidence_id}")
        self.evidence[evidence_id] = evidence
        self.hash_log.append({"evidence_id": evidence_id, "hash": data_hash, "time": datetime.now().isoformat()})
        return evidence

    def verify_integrity(self, evidence_id: str, current_data: str) -> bool:
        evidence = self.evidence.get(evidence_id)
        if not evidence:
            return False
        current_hash = hashlib.sha256(current_data.encode()).hexdigest()
        is_valid = current_hash == evidence.data_hash
        if not is_valid:
            evidence.tamper_detected = True
        return is_valid

    def get_evidence(self, evidence_id: str) -> Optional[CollectedEvidence]:
        return self.evidence.get(evidence_id)

    def get_all_evidence(self) -> List[CollectedEvidence]:
        return list(self.evidence.values())

    def get_tampered(self) -> List[CollectedEvidence]:
        return [e for e in self.evidence.values() if e.tamper_detected]

    def delete_evidence(self, evidence_id: str) -> bool:
        if evidence_id in self.evidence:
            del self.evidence[evidence_id]
            return True
        return False

    def count(self) -> int:
        return len(self.evidence)
