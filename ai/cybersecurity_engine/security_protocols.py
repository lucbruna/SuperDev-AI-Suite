"""Cybersecurity Engine Protocols — Protocol definitions for security operations."""
from dataclasses import dataclass, field
from enum import Enum


class SecurityProtocolType(Enum):
    TLS = "tls"
    IPSec = "ipsec"
    SSH = "ssh"
    HTTPS = "https"
    WSS = "wss"


@dataclass
class SecurityProtocolConfig:
    name: str
    protocol_type: SecurityProtocolType = SecurityProtocolType.TLS
    version: str = "1.3"
    cipher_suites: list[str] = field(default_factory=lambda: ["AES-256-GCM", "ChaCha20-Poly1305"])
    certificate_required: bool = True
    min_key_length: int = 256
