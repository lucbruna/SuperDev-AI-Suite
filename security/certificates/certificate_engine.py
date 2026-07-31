"""Certificates subsystem (Volume 16) — lifecycle, fingerprint, expiry."""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import Any

from ..security_models import CertificateInfo


class CertificateEngine:
    """Manage certificates: issue, validate, list, rotate."""

    name = "certificates"
    description = "Certificate lifecycle, validation and rotation"

    def __init__(self, engine: Any | None = None) -> None:
        self.engine = engine
        self._certificates: dict[str, CertificateInfo] = {}

    def issue(
        self,
        subject: str,
        issuer: str = "superdev-ca",
        validity_days: int = 365,
        public_key: str = "",
    ) -> CertificateInfo:
        """Create a certificate and register it in the engine store."""
        now = time.time()
        cert = CertificateInfo(
            serial=uuid.uuid4().hex[:16],
            subject=subject,
            issuer=issuer,
            not_before=now,
            not_after=now + max(1, validity_days) * 86400,
            fingerprint=hashlib.sha256(f"{subject}:{issuer}:{now}".encode()).hexdigest()[
                :32
            ],
            public_key=public_key,
        )
        self._certificates[cert.serial] = cert
        if self.engine is not None:
            self.engine.metrics.increment("security.certificates_issued")
            self.engine.registry.register_certificate(cert)
        return cert

    def get(self, serial: str) -> CertificateInfo | None:
        return self._certificates.get(serial)

    def list(self) -> list[CertificateInfo]:
        return list(self._certificates.values())

    def validate(self, serial: str) -> dict[str, Any]:
        """Validate a certificate: known, not expired, fingerprint present."""
        cert = self._certificates.get(serial)
        if cert is None:
            return {"valid": False, "reason": "unknown certificate", "serial": serial}
        expired = cert.is_expired()
        valid = not expired and bool(cert.fingerprint)
        if self.engine is not None:
            self.engine.metrics.increment(
                "security.certificate_validations",
                labels={"result": "valid" if valid else "invalid"},
            )
        return {
            "valid": valid,
            "expired": expired,
            "subject": cert.subject,
            "serial": serial,
            "reason": "expired" if expired else "ok",
        }

    def rotate(self, serial: str, validity_days: int = 365) -> CertificateInfo | None:
        """Re-issue a certificate with a fresh serial for the same subject."""
        cert = self._certificates.get(serial)
        if cert is None:
            return None
        new_cert = self.issue(
            subject=cert.subject,
            issuer=cert.issuer,
            validity_days=validity_days,
            public_key=cert.public_key,
        )
        if self.engine is not None:
            self.engine.metrics.increment("security.certificates_rotated")
        return new_cert

    def expires_within(self, days: int) -> list[CertificateInfo]:
        horizon = time.time() + max(0, days) * 86400
        return [c for c in self._certificates.values() if c.not_after <= horizon]

    def status(self) -> dict[str, Any]:
        return {
            "certificates": len(self._certificates),
            "expired": sum(1 for c in self._certificates.values() if c.is_expired()),
        }


__all__ = ["CertificateEngine"]
