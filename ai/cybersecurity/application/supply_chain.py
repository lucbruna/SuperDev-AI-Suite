"""
Software Supply Chain Security
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import secrets


class IntegrityStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"


@dataclass
class SBOMComponent:
    name: str
    version: str
    supplier: str = ""
    license: str = ""
    hash_sha256: str = ""
    purl: str = ""


@dataclass
class SBOMDocument:
    doc_id: str
    components: List[SBOMComponent] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    format: str = "spdx"
    tool: str = "superdev-scanner"


@dataclass
class IntegrityCheck:
    component: str
    status: IntegrityStatus
    expected_hash: str = ""
    actual_hash: str = ""
    verified_at: datetime = field(default_factory=datetime.now)


class SupplyChainSecurity:
    def __init__(self):
        self.sboms: List[SBOMDocument] = []
        self.integrity_checks: List[IntegrityCheck] = []
        self.provenance: Dict[str, Dict[str, Any]] = {}

    def generate_sbom(self, components: List[Dict[str, str]]) -> SBOMDocument:
        doc = SBOMDocument(doc_id=secrets.token_hex(16))
        for comp in components:
            sbom_comp = SBOMComponent(name=comp.get("name", ""), version=comp.get("version", ""), supplier=comp.get("supplier", ""), license=comp.get("license", ""))
            doc.components.append(sbom_comp)
        self.sboms.append(doc)
        return doc

    def verify_integrity(self, component: str, expected_hash: str, actual_hash: str) -> IntegrityCheck:
        status = IntegrityStatus.VALID if expected_hash == actual_hash else IntegrityStatus.INVALID
        check = IntegrityCheck(component=component, status=status, expected_hash=expected_hash, actual_hash=actual_hash)
        self.integrity_checks.append(check)
        return check

    def record_provenance(self, component: str, source: str, commit: str, build_id: str) -> None:
        self.provenance[component] = {"source": source, "commit": commit, "build_id": build_id, "recorded_at": datetime.now().isoformat()}

    def get_provenance(self, component: str) -> Optional[Dict[str, Any]]:
        return self.provenance.get(component)

    def get_sbom(self, doc_id: str) -> Optional[SBOMDocument]:
        for doc in self.sboms:
            if doc.doc_id == doc_id:
                return doc
        return None

    def get_invalid_integrity(self) -> List[IntegrityCheck]:
        return [c for c in self.integrity_checks if c.status == IntegrityStatus.INVALID]

    def count_components(self) -> int:
        return sum(len(doc.components) for doc in self.sboms)

    def count(self) -> int:
        return len(self.sboms)
