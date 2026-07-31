"""
Certificate Management
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import secrets


class CertStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    PENDING = "pending"


@dataclass
class Certificate:
    cert_id: str
    subject: str
    issuer: str
    not_before: datetime = field(default_factory=datetime.now)
    not_after: Optional[datetime] = None
    serial_number: str = ""
    fingerprint: str = ""
    status: CertStatus = CertStatus.ACTIVE
    san: List[str] = field(default_factory=list)
    key_usage: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CertificateManager:
    def __init__(self):
        self.certificates: Dict[str, Certificate] = {}
        self.revoked_serials: set = set()

    def generate_self_signed(self, subject: str, valid_days: int = 365) -> Certificate:
        cert_id = secrets.token_hex(16)
        serial = secrets.token_hex(20)
        fp = hashlib.sha256(subject.encode()).hexdigest()[:32]
        cert = Certificate(
            cert_id=cert_id, subject=subject, issuer=subject,
            serial_number=serial, fingerprint=fp,
            key_usage=["digital_signature", "key_encipherment"]
        )
        self.certificates[cert_id] = cert
        return cert

    def sign_certificate(self, subject: str, issuer_cert_id: str) -> Certificate:
        issuer = self.certificates.get(issuer_cert_id)
        if not issuer:
            raise ValueError(f"Issuer {issuer_cert_id} not found")
        cert_id = secrets.token_hex(16)
        cert = Certificate(cert_id=cert_id, subject=subject, issuer=issuer.subject)
        self.certificates[cert_id] = cert
        return cert

    def revoke_certificate(self, cert_id: str) -> bool:
        cert = self.certificates.get(cert_id)
        if cert:
            cert.status = CertStatus.REVOKED
            self.revoked_serials.add(cert.serial_number)
            return True
        return False

    def verify_certificate(self, cert_id: str) -> bool:
        cert = self.certificates.get(cert_id)
        if not cert:
            return False
        if cert.status != CertStatus.ACTIVE:
            return False
        if cert.serial_number in self.revoked_serials:
            return False
        return True

    def get_certificate(self, cert_id: str) -> Optional[Certificate]:
        return self.certificates.get(cert_id)

    def find_by_subject(self, subject: str) -> List[Certificate]:
        return [c for c in self.certificates.values() if c.subject == subject]

    def list_active(self) -> List[Certificate]:
        return [c for c in self.certificates.values() if c.status == CertStatus.ACTIVE]

    def count(self) -> int:
        return len(self.certificates)
