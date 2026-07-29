"""
Multimodal Security - Privacy, access control, data masking, and consent management.
"""

from __future__ import annotations

import hashlib
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from .multimodal_config import MultimodalConfig

logger = logging.getLogger(__name__)


class ConsentManager:
    def __init__(self, config: MultimodalConfig):
        self._config = config
        self._consents: Dict[str, Dict[str, Any]] = {}

    def register_consent(self, user_id: str, modality: str, purpose: str, granted: bool = True) -> Dict[str, Any]:
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "modality": modality,
            "purpose": purpose,
            "granted": granted,
            "granted_at": datetime.utcnow().isoformat() if granted else None,
            "revoked_at": None if granted else datetime.utcnow().isoformat(),
        }
        key = f"{user_id}:{modality}:{purpose}"
        self._consents[key] = record
        return record

    def check(self, user_id: str, modality: str, purpose: str) -> bool:
        key = f"{user_id}:{modality}:{purpose}"
        record = self._consents.get(key)
        if record is None:
            return False
        return record.get("granted", False) and record.get("revoked_at") is None

    def revoke(self, user_id: str, modality: str, purpose: str) -> bool:
        key = f"{user_id}:{modality}:{purpose}"
        record = self._consents.get(key)
        if record is None:
            return False
        record["granted"] = False
        record["revoked_at"] = datetime.utcnow().isoformat()
        return True

    def list_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        return [v for k, v in self._consents.items() if v["user_id"] == user_id]

    def get_summary(self, user_id: str) -> Dict[str, Any]:
        consents = self.list_for_user(user_id)
        return {
            "user_id": user_id,
            "total": len(consents),
            "granted": sum(1 for c in consents if c["granted"]),
            "revoked": sum(1 for c in consents if not c["granted"]),
            "modalities": list(set(c["modality"] for c in consents if c["granted"])),
        }


class PrivacyManager:
    def __init__(self, config: MultimodalConfig):
        self._config = config
        self._pii_patterns = {
            "email": r'[\w\.-]+@[\w\.-]+\.\w+',
            "phone": r'\+?\d[\d\s\-\(\)]{7,}\d',
            "ssn": r'\d{3}-\d{2}-\d{4}',
            "credit_card": r'\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}',
            "ip_address": r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            "location": r'\-?\d+\.\d+,\s*\-?\d+\.\d+',
        }

    def mask_email(self, email: str) -> str:
        parts = email.split("@")
        if len(parts) != 2:
            return email
        name = parts[0]
        masked = name[0] + "***" + name[-1] if len(name) > 2 else name[0] + "***"
        return masked + "@" + parts[1]

    def mask_phone(self, phone: str) -> str:
        digits = re.sub(r'\D', '', phone)
        if len(digits) >= 10:
            return digits[:2] + "****" + digits[-4:]
        return "****"

    def mask_ssn(self, ssn: str) -> str:
        digits = re.sub(r'\D', '', ssn)
        if len(digits) == 9:
            return "***-**-" + digits[-4:]
        return "***-**-****"

    def mask_text(self, text: str) -> str:
        result = text
        for pii_type, pattern in self._pii_patterns.items():
            result = re.sub(pattern, f"[{pii_type.upper()}_REDACTED]", result)
        return result

    def detect_pii(self, text: str) -> Dict[str, List[str]]:
        found: Dict[str, List[str]] = {}
        for pii_type, pattern in self._pii_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                found[pii_type] = matches
        return found

    def anonymize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for k, v in data.items():
            if k in ("email", "e_mail") and isinstance(v, str):
                result[k] = self.mask_email(v)
            elif k in ("phone", "phone_number", "celular") and isinstance(v, str):
                result[k] = self.mask_phone(v)
            elif k in ("ssn", "cpf", "tax_id") and isinstance(v, str):
                result[k] = self.mask_ssn(v)
            elif k in ("name", "full_name") and isinstance(v, str):
                parts = v.split()
                result[k] = parts[0] + " " + " ".join(p[0] + "." for p in parts[1:]) if len(parts) > 1 else parts[0]
            else:
                result[k] = v
        return result


class DataMasker:
    def __init__(self):
        self._mask_rules: Dict[str, str] = {}

    def add_rule(self, field_name: str, mask_char: str = "*") -> None:
        self._mask_rules[field_name] = mask_char

    def remove_rule(self, field_name: str) -> None:
        self._mask_rules.pop(field_name, None)

    def mask_field(self, value: str, mask_char: str = "*") -> str:
        if len(value) <= 4:
            return mask_char * len(value)
        return value[:2] + mask_char * (len(value) - 4) + value[-2:]

    def mask_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for k, v in data.items():
            if k in self._mask_rules and isinstance(v, str):
                result[k] = self.mask_field(v, self._mask_rules[k])
            else:
                result[k] = v
        return result

    def mask_audio_transcript(self, transcript: str, sensitive_words: List[str]) -> str:
        result = transcript
        for word in sensitive_words:
            result = re.sub(re.escape(word), "*" * len(word), result, flags=re.IGNORECASE)
        return result

    def mask_image_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        sensitive_keys = {"gps", "gps_latitude", "gps_longitude", "location", "device_id", "serial"}
        result = {}
        for k, v in metadata.items():
            if k.lower() in sensitive_keys:
                result[k] = "[REDACTED]"
            else:
                result[k] = v
        return result


class AccessControl:
    def __init__(self):
        self._roles: Dict[str, Set[str]] = {
            "admin": {"text:read", "text:write", "voice:read", "voice:write", "vision:read", "vision:write",
                      "video:read", "video:write", "document:read", "document:write", "sensor:read", "sensor:write",
                      "security:configure", "security:audit", "consent:manage"},
            "analyst": {"text:read", "voice:read", "vision:read", "video:read", "document:read", "sensor:read"},
            "operator": {"text:read", "text:write", "voice:read", "document:read", "document:write"},
            "viewer": {"text:read", "document:read"},
            "auditor": {"text:read", "voice:read", "document:read", "security:audit"},
        }
        self._permissions: Dict[str, Dict[str, str]] = {}

    def set_user_role(self, user_id: str, role: str) -> None:
        if role not in self._roles:
            raise ValueError(f"Invalid role: {role}")
        self._permissions[user_id] = {"role": role}

    def get_user_role(self, user_id: str) -> Optional[str]:
        entry = self._permissions.get(user_id)
        return entry.get("role") if entry else None

    def check_access(self, user_id: str, modality: str, action: str) -> bool:
        entry = self._permissions.get(user_id)
        if not entry:
            return False
        role = entry.get("role", "")
        required = f"{modality}:{action}"
        return required in self._roles.get(role, set())

    def has_modality_access(self, user_id: str, modality: str) -> bool:
        return self.check_access(user_id, modality, "read") or self.check_access(user_id, modality, "write")

    def list_roles(self) -> List[str]:
        return list(self._roles.keys())

    def list_permissions_for_role(self, role: str) -> Set[str]:
        return self._roles.get(role, set())


class MultimodalSecurityManager:
    def __init__(self, config: Optional[MultimodalConfig] = None):
        self._config = config or MultimodalConfig()
        self._consent = ConsentManager(self._config)
        self._privacy = PrivacyManager(self._config)
        self._masker = DataMasker()
        self._access = AccessControl()
        self._audit_log: List[Dict[str, Any]] = []
        self._anonymization_enabled = True
        self._encryption_enabled = True

    @property
    def consent(self) -> ConsentManager:
        return self._consent

    @property
    def privacy(self) -> PrivacyManager:
        return self._privacy

    @property
    def masker(self) -> DataMasker:
        return self._masker

    @property
    def access(self) -> AccessControl:
        return self._access

    def enable_anonymization(self, enabled: bool) -> None:
        self._anonymization_enabled = enabled

    def enable_encryption(self, enabled: bool) -> None:
        self._encryption_enabled = enabled

    def verify_access(self, user_id: str, modality: str, action: str) -> bool:
        allowed = self._access.check_access(user_id, modality, action)
        self._log_access(user_id, modality, action, "granted" if allowed else "denied")
        return allowed

    def verify_consent(self, user_id: str, modality: str, purpose: str) -> bool:
        return self._consent.check(user_id, modality, purpose)

    def sanitize_input(self, text: str) -> str:
        if self._anonymization_enabled:
            return self._privacy.mask_text(text)
        return text

    def sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        if self._anonymization_enabled:
            return self._masker.mask_image_metadata(metadata)
        return metadata

    def _log_access(self, user_id: str, modality: str, action: str, status: str) -> None:
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "modality": modality,
            "action": action,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._audit_log.append(record)
        if len(self._audit_log) > 10000:
            self._audit_log = self._audit_log[-5000:]

    def get_audit_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._audit_log[-limit:]

    def get_security_report(self) -> Dict[str, Any]:
        return {
            "anonymization_enabled": self._anonymization_enabled,
            "encryption_enabled": self._encryption_enabled,
            "access_control_active": True,
            "consent_management_active": True,
            "audit_trail_size": len(self._audit_log),
            "roles": self._access.list_roles(),
            "modalities": ["text", "voice", "vision", "video", "document", "sensor"],
        }
