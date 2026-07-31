"""Privacy engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from enum import Enum
import time, uuid, hashlib

class DataCategory(Enum):
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    FINANCIAL = "financial"
    HEALTH = "health"
    BIOMETRIC = "biometric"
    BEHAVIORAL = "behavioral"
    LOCATION = "location"
    DEVICE = "device"

class ConsentRecord:
    def __init__(self, user_id: str, purpose: str, granted: bool) -> None:
        self.consent_id = str(uuid.uuid4())[:8]
        self.user_id = user_id
        self.purpose = purpose
        self.granted = granted
        self.timestamp = time.time()

class PrivacyEngine:
    def __init__(self) -> None:
        self._consent_records: Dict[str, ConsentRecord] = {}
        self._data_inventory: Dict[str, Dict[str, Any]] = {}
        self._anonymization_log: List[Dict[str, Any]] = []
    def record_consent(self, user_id: str, purpose: str, granted: bool) -> ConsentRecord:
        record = ConsentRecord(user_id, purpose, granted)
        self._consent_records[record.consent_id] = record
        return record
    def has_consent(self, user_id: str, purpose: str) -> bool:
        for r in self._consent_records.values():
            if r.user_id == user_id and r.purpose == purpose and r.granted:
                return True
        return False
    def withdraw_consent(self, user_id: str, purpose: str) -> bool:
        for r in self._consent_records.values():
            if r.user_id == user_id and r.purpose == purpose:
                r.granted = False
                return True
        return False
    def register_data(self, data_id: str, category: DataCategory, owner: str = "", location: str = "") -> None:
        self._data_inventory[data_id] = {"category": category.value, "owner": owner, "location": location, "registered_at": time.time()}
    def anonymize(self, data: str, method: str = "hash") -> Dict[str, Any]:
        if method == "hash":
            anonymized = hashlib.sha256(data.encode()).hexdigest()[:16]
        elif method == "mask":
            anonymized = data[:2] + "***" + data[-2:] if len(data) > 4 else "***"
        elif method == "remove":
            anonymized = ""
        else:
            anonymized = data
        self._anonymization_log.append({"original_length": len(data), "method": method, "timestamp": time.time()})
        return {"anonymized": anonymized, "method": method}
    def get_user_consent(self, user_id: str) -> List[Dict[str, Any]]:
        return [{"consent_id": r.consent_id, "purpose": r.purpose, "granted": r.granted, "timestamp": r.timestamp} for r in self._consent_records.values() if r.user_id == user_id]
    def get_data_inventory(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._data_inventory)
    def list_categories(self) -> List[str]:
        return [c.value for c in DataCategory]
