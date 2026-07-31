"""Configuration for the Security Engine (Volume 16)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class SecurityConfig:
    """Central configuration for the Security Engine subsystems."""

    enabled: bool = True
    encryption_algorithm: str = "aes-256-gcm"
    hashing_algorithm: str = "sha256"
    signature_algorithm: str = "ed25519"
    cert_validity_days: int = 365
    vault_secret_ttl_hours: int = 24
    min_password_length: int = 12
    require_mfa: bool = True
    session_timeout_minutes: int = 30
    max_failed_logins: int = 5
    integrity_check_interval: int = 3600
    compliance_standards: list[str] = field(
        default_factory=lambda: ["SOC2", "GDPR", "HIPAA"]
    )
    scan_timeout_seconds: int = 120
    threat_lookback_hours: int = 24
    audit_enabled: bool = True
    crypto_key_rotation_days: int = 90
    allowed_cipher_suites: list[str] = field(
        default_factory=lambda: ["TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"]
    )

    @classmethod
    def default(cls) -> SecurityConfig:
        return cls()

    @classmethod
    def from_env(cls) -> SecurityConfig:
        """Build a config honoring common environment variables."""
        return cls(
            enabled=os.getenv("SUPERDEV_SECURITY_ENABLED", "1") != "0",
            encryption_algorithm=os.getenv(
                "SUPERDEV_SECURITY_ENCRYPTION", "aes-256-gcm"
            ),
            hashing_algorithm=os.getenv("SUPERDEV_SECURITY_HASHING", "sha256"),
            min_password_length=int(os.getenv("SUPERDEV_SECURITY_MIN_PASSWORD", "12")),
            require_mfa=os.getenv("SUPERDEV_SECURITY_MFA", "1") != "0",
        )
