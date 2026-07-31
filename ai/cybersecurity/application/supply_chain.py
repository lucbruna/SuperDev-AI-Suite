"""
Software Supply Chain Security
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
    components: list[SBOMComponent] = field(default_factory=list)
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
        self.sboms: list[SBOMDocument] = []
        self.integrity_checks: list[IntegrityCheck] = []
        self.provenance: dict[str, dict[str, Any]] = {}

    def generate_sbom(self, components: list[dict[str, str]]) -> SBOMDocument:
        doc = SBOMDocument(doc_id=secrets.token_hex(16))
        for comp in components:
            sbom_comp = SBOMComponent(
                name=comp.get("name", ""),
                version=comp.get("version", ""),
                supplier=comp.get("supplier", ""),
                license=comp.get("license", ""),
            )
            doc.components.append(sbom_comp)
        self.sboms.append(doc)
        return doc

    def verify_integrity(self, component: str, expected_hash: str, actual_hash: str) -> IntegrityCheck:
        status = IntegrityStatus.VALID if expected_hash == actual_hash else IntegrityStatus.INVALID
        check = IntegrityCheck(component=component, status=status, expected_hash=expected_hash, actual_hash=actual_hash)
        self.integrity_checks.append(check)
        return check

    def record_provenance(self, component: str, source: str, commit: str, build_id: str) -> None:
        self.provenance[component] = {
            "source": source,
            "commit": commit,
            "build_id": build_id,
            "recorded_at": datetime.now().isoformat(),
        }

    def get_provenance(self, component: str) -> dict[str, Any] | None:
        return self.provenance.get(component)

    def get_sbom(self, doc_id: str) -> SBOMDocument | None:
        for doc in self.sboms:
            if doc.doc_id == doc_id:
                return doc
        return None

    def get_invalid_integrity(self) -> list[IntegrityCheck]:
        return [c for c in self.integrity_checks if c.status == IntegrityStatus.INVALID]

    def count_components(self) -> int:
        return sum(len(doc.components) for doc in self.sboms)

    def count(self) -> int:
        return len(self.sboms)
