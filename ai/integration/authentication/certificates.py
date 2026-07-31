"""
Certificate Management for Integrations
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class Certificate:
    cert_id: str
    name: str
    cert_type: str = "client"
    subject: str = ""
    issuer: str = ""
    fingerprint: str = ""
    is_active: bool = True
    expires_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


class CertificateManager:
    def __init__(self):
        self.certificates: Dict[str, Certificate] = {}

    def register_certificate(self, name: str, cert_type: str = "client", subject: str = "", fingerprint: str = "", **kwargs) -> Certificate:
        cert_id = hashlib.sha256(f"{name}{cert_type}".encode()).hexdigest()[:16]
        cert = Certificate(cert_id=cert_id, name=name, cert_type=cert_type, subject=subject, fingerprint=fingerprint, **kwargs)
        self.certificates[cert_id] = cert
        return cert

    def validate_certificate(self, cert_id: str) -> bool:
        cert = self.certificates.get(cert_id)
        if not cert or not cert.is_active:
            return False
        if cert.expires_at and datetime.now() > cert.expires_at:
            return False
        return True

    def revoke_certificate(self, cert_id: str) -> bool:
        cert = self.certificates.get(cert_id)
        if cert:
            cert.is_active = False
            return True
        return False

    def get_certificate(self, cert_id: str) -> Optional[Certificate]:
        return self.certificates.get(cert_id)

    def list_certificates(self) -> List[Certificate]:
        return list(self.certificates.values())

    def count(self) -> int:
        return len(self.certificates)
