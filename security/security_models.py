"""Data models for the Security Engine (Volume 16)."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum


class CryptoAlgorithm(StrEnum):
    AES256GCM = "aes-256-gcm"
    AES256CBC = "aes-256-cbc"
    CHACHA20 = "chacha20"


class HashAlgorithm(StrEnum):
    SHA256 = "sha256"
    SHA512 = "sha512"
    BLAKE2B = "blake2b"


class SignatureAlgorithm(StrEnum):
    ED25519 = "ed25519"
    RSA = "rsa"
    ECDSA = "ecdsa"


class ComplianceStatus(StrEnum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING = "pending"
    NOT_APPLICABLE = "not_applicable"


class ThreatSeverity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ThreatStatus(StrEnum):
    DETECTED = "detected"
    ANALYZED = "analyzed"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"


@dataclass
class EncryptedPayload:
    """Result of an encryption operation."""

    ciphertext: str
    nonce: str
    algorithm: str
    key_id: str
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, str | float]:
        return {
            "ciphertext": self.ciphertext,
            "nonce": self.nonce,
            "algorithm": self.algorithm,
            "key_id": self.key_id,
            "created_at": self.created_at,
        }


@dataclass
class HashResult:
    """Result of a hashing operation."""

    digest: str
    algorithm: str
    salt: str = ""
    iterations: int = 1

    def to_dict(self) -> dict[str, str | int]:
        return {
            "digest": self.digest,
            "algorithm": self.algorithm,
            "salt": self.salt,
            "iterations": self.iterations,
        }


@dataclass
class SignatureResult:
    """Result of a signing / verification operation."""

    signature: str
    algorithm: str
    public_key: str = ""
    valid: bool = True
    error: str = ""

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "signature": self.signature,
            "algorithm": self.algorithm,
            "public_key": self.public_key,
            "valid": self.valid,
            "error": self.error,
        }


@dataclass
class CertificateInfo:
    """X.509-like certificate summary."""

    serial: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    subject: str = ""
    issuer: str = ""
    not_before: float = field(default_factory=time.time)
    not_after: float = field(default_factory=lambda: time.time() + 31536000)
    fingerprint: str = ""
    public_key: str = ""
    valid: bool = True

    def is_expired(self) -> bool:
        return time.time() > self.not_after

    def to_dict(self) -> dict[str, str | float | bool]:
        return {
            "serial": self.serial,
            "subject": self.subject,
            "issuer": self.issuer,
            "not_before": self.not_before,
            "not_after": self.not_after,
            "fingerprint": self.fingerprint,
            "valid": self.valid,
        }


@dataclass
class VaultSecret:
    """A secret stored in the vault."""

    name: str
    value: str
    owner: str = "system"
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    version: int = 1
    rotation_due: float | None = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        # ``>=`` para cobrir relógios de baixa resolução (Windows): duas
        # chamadas a time.time() no mesmo tick retornam o mesmo valor.
        return time.time() >= self.expires_at

    def to_dict(self) -> dict[str, str | float | int | None]:
        return {
            "name": self.name,
            "owner": self.owner,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "version": self.version,
            "rotation_due": self.rotation_due,
        }


@dataclass
class IntegrityReport:
    """Report of a file/artifact integrity check."""

    target: str
    status: str = "ok"  # ok | modified | missing | error
    checksum: str = ""
    expected_checksum: str = ""
    changed_files: list[str] = field(default_factory=list)
    checked_at: float = field(default_factory=time.time)
    error: str = ""

    def to_dict(self) -> dict[str, str | float | list[str]]:
        return {
            "target": self.target,
            "status": self.status,
            "checksum": self.checksum,
            "expected_checksum": self.expected_checksum,
            "changed_files": self.changed_files,
            "checked_at": self.checked_at,
            "error": self.error,
        }


@dataclass
class ComplianceResult:
    """Result of a compliance evaluation against a standard."""

    standard: str
    status: ComplianceStatus = ComplianceStatus.PENDING
    score: float = 0.0
    controls: list[dict[str, object]] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    evaluated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, object]:
        return {
            "standard": self.standard,
            "status": self.status.value,
            "score": self.score,
            "controls": self.controls,
            "gaps": self.gaps,
            "evaluated_at": self.evaluated_at,
        }


@dataclass
class SecurityScanResult:
    """Aggregated result of a full security scan."""

    target: str
    reports: list[object] = field(default_factory=list)
    total_findings: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    risk_score: float = 0.0
    scanned_at: float = field(default_factory=time.time)
    error: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "total_findings": self.total_findings,
            "critical": self.critical_count,
            "high": self.high_count,
            "medium": self.medium_count,
            "low": self.low_count,
            "risk_score": self.risk_score,
            "scanned_at": self.scanned_at,
            "error": self.error,
        }


@dataclass
class ThreatEvent:
    """A detected threat / anomaly."""

    threat_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    title: str = ""
    source: str = ""
    severity: ThreatSeverity = ThreatSeverity.LOW
    details: dict[str, object] = field(default_factory=dict)
    status: ThreatStatus = ThreatStatus.DETECTED
    detected_at: float = field(default_factory=time.time)
    mitigated: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "threat_id": self.threat_id,
            "title": self.title,
            "source": self.source,
            "severity": self.severity.value,
            "details": self.details,
            "status": self.status.value,
            "detected_at": self.detected_at,
            "mitigated": self.mitigated,
        }
