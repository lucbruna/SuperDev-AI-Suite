"""
Privacy Compliance Manager (GDPR/CCPA)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ConsentType(Enum):
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    THIRD_PARTY = "third_party"
    ESSENTIAL = "essential"


class DataSubjectRequest(Enum):
    ACCESS = "access"
    DELETION = "deletion"
    PORTABILITY = "portability"
    RECTIFICATION = "rectification"
    RESTRICTION = "restriction"
    OBJECTION = "objection"


class ConsentStatus(Enum):
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


@dataclass
class Consent:
    consent_id: str
    user_id: str
    consent_type: ConsentType
    status: ConsentStatus = ConsentStatus.GRANTED
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    ip_address: str = ""
    method: str = "web_form"


@dataclass
class DataSubjectRequestRecord:
    request_id: str
    user_id: str
    request_type: DataSubjectRequest
    status: str = "pending"
    submitted_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    notes: str = ""


class PrivacyManager:
    def __init__(self):
        self.consents: dict[str, Consent] = {}
        self.dsar_records: dict[str, DataSubjectRequestRecord] = {}
        self.data_processing: list[dict[str, Any]] = []

    def record_consent(
        self, user_id: str, consent_type: ConsentType, granted: bool = True, ip_address: str = ""
    ) -> Consent:
        consent_id = f"consent_{user_id}_{consent_type.value}"
        status = ConsentStatus.GRANTED if granted else ConsentStatus.DENIED
        consent = Consent(
            consent_id=consent_id, user_id=user_id, consent_type=consent_type, status=status, ip_address=ip_address
        )
        self.consents[consent_id] = consent
        return consent

    def withdraw_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        for consent in self.consents.values():
            if consent.user_id == user_id and consent.consent_type == consent_type:
                consent.status = ConsentStatus.WITHDRAWN
                return True
        return False

    def has_consent(self, user_id: str, consent_type: ConsentType) -> bool:
        for consent in self.consents.values():
            if consent.user_id == user_id and consent.consent_type == consent_type:
                return consent.status == ConsentStatus.GRANTED
        return False

    def submit_dsar(self, user_id: str, request_type: DataSubjectRequest) -> DataSubjectRequestRecord:
        request_id = f"dsar_{len(self.dsar_records)}"
        record = DataSubjectRequestRecord(request_id=request_id, user_id=user_id, request_type=request_type)
        self.dsar_records[request_id] = record
        return record

    def complete_dsar(self, request_id: str) -> bool:
        record = self.dsar_records.get(request_id)
        if record:
            record.status = "completed"
            record.completed_at = datetime.now()
            return True
        return False

    def get_user_consents(self, user_id: str) -> list[Consent]:
        return [c for c in self.consents.values() if c.user_id == user_id]

    def get_pending_dsars(self) -> list[DataSubjectRequestRecord]:
        return [r for r in self.dsar_records.values() if r.status == "pending"]

    def log_processing(self, purpose: str, data_categories: list[str], legal_basis: str = "") -> None:
        self.data_processing.append(
            {
                "purpose": purpose,
                "categories": data_categories,
                "legal_basis": legal_basis,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def count(self) -> int:
        return len(self.consents)
