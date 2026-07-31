"""
Security Configuration
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EncryptionAlgorithm(Enum):
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    RSA_4096 = "rsa_4096"
    CHACHA20 = "chacha20"


@dataclass
class SecurityConfig:
    security_level: SecurityLevel = SecurityLevel.HIGH
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    max_login_attempts: int = 5
    lockout_duration: int = 300
    session_timeout: int = 3600
    mfa_required: bool = True
    password_min_length: int = 12
    password_require_uppercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = True
    audit_all_actions: bool = True
    threat_detection_enabled: bool = True
    auto_incident_response: bool = True
    compliance_mode: str = "soc2"
    ai_security_enabled: bool = True
    prompt_injection_protection: bool = True
    model_protection: bool = True
    code_scanning_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "security_level": self.security_level.value,
            "encryption_algorithm": self.encryption_algorithm.value,
            "mfa_required": self.mfa_required,
            "threat_detection_enabled": self.threat_detection_enabled,
            "ai_security_enabled": self.ai_security_enabled,
        }


@dataclass
class PolicyRule:
    name: str
    action: str = "allow"
    conditions: dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    enabled: bool = True


@dataclass
class SecurityPolicy:
    name: str
    rules: list[PolicyRule] = field(default_factory=list)
    enabled: bool = True

    def add_rule(self, rule: PolicyRule) -> None:
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r.priority, reverse=True)

    def evaluate(self, context: dict[str, Any]) -> str:
        for rule in self.rules:
            if not rule.enabled:
                continue
            if self._match_conditions(rule.conditions, context):
                return rule.action
        return "deny"

    def _match_conditions(self, conditions: dict, context: dict) -> bool:
        for key, value in conditions.items():
            if key not in context:
                return False
            if isinstance(value, list):
                if context[key] not in value:
                    return False
            elif context[key] != value:
                return False
        return True
