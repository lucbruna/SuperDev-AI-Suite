"""Certificate management."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time, hashlib, secrets

class Certificate:
    def __init__(self, cert_id: str, subject: str, issuer: str = "self", valid_days: int = 365) -> None:
        self.cert_id = cert_id
        self.subject = subject
        self.issuer = issuer
        self.created_at = time.time()
        self.expires_at = self.created_at + (valid_days * 86400)
        self.fingerprint = hashlib.sha256((cert_id + subject).encode()).hexdigest()[:16]
        self.revoked = False

class CertificateManager:
    def __init__(self) -> None:
        self._certificates: Dict[str, Certificate] = {}
        self._ca_cert: Optional[Certificate] = None
    def create_certificate(self, cert_id: str, subject: str, valid_days: int = 365) -> Certificate:
        issuer = self._ca_cert.subject if self._ca_cert else "self-signed"
        cert = Certificate(cert_id, subject, issuer, valid_days)
        self._certificates[cert_id] = cert
        return cert
    def get_certificate(self, cert_id: str) -> Optional[Certificate]:
        cert = self._certificates.get(cert_id)
        if cert and not cert.revoked and cert.expires_at > time.time():
            return cert
        return None
    def revoke_certificate(self, cert_id: str) -> bool:
        if cert_id in self._certificates:
            self._certificates[cert_id].revoked = True
            return True
        return False
    def verify_certificate(self, cert_id: str) -> Dict[str, Any]:
        cert = self._certificates.get(cert_id)
        if not cert:
            return {"valid": False, "error": "not_found"}
        if cert.revoked:
            return {"valid": False, "error": "revoked"}
        if cert.expires_at < time.time():
            return {"valid": False, "error": "expired"}
        return {"valid": True, "subject": cert.subject, "fingerprint": cert.fingerprint}
    def list_certificates(self) -> List[str]:
        return list(self._certificates.keys())
    def set_ca(self, cert_id: str, subject: str) -> Certificate:
        self._ca_cert = Certificate(cert_id, subject, "self", valid_days=3650)
        self._certificates[cert_id] = self._ca_cert
        return self._ca_cert
