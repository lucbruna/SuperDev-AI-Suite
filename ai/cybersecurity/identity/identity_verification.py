"""
Identity Verification
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class VerificationMethod(Enum):
    EMAIL = "email"
    PHONE = "phone"
    DOCUMENT = "document"
    BIOMETRIC = "biometric"
    KNOWLEDGE = "knowledge"


@dataclass
class VerificationRecord:
    identity_id: str
    method: VerificationMethod
    verified: bool = False
    verified_at: str | None = None
    expires_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class IdentityVerifier:
    def __init__(self):
        self.verifications: dict[str, VerificationRecord] = {}

    def verify(self, identity_id: str, method: VerificationMethod, **kwargs) -> VerificationRecord:
        record = VerificationRecord(
            identity_id=identity_id,
            method=method,
            verified=True,
            verified_at=kwargs.get("verified_at"),
            metadata=kwargs.get("metadata", {})
        )
        key = f"{identity_id}:{method.value}"
        self.verifications[key] = record
        return record

    def is_verified(self, identity_id: str, method: VerificationMethod) -> bool:
        key = f"{identity_id}:{method.value}"
        record = self.verifications.get(key)
        return record.verified if record else False

    def get_verification(self, identity_id: str, method: VerificationMethod) -> VerificationRecord | None:
        key = f"{identity_id}:{method.value}"
        return self.verifications.get(key)

    def revoke(self, identity_id: str, method: VerificationMethod) -> bool:
        key = f"{identity_id}:{method.value}"
        if key in self.verifications:
            del self.verifications[key]
            return True
        return False
