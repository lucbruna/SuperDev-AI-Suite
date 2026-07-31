"""Fingerprint - Fingerprint biometric module."""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib


@dataclass
class FingerprintTemplate:
    template_id: str
    user_id: str
    finger_id: int = 0
    template_data: str = ""
    quality: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True


class FingerprintManager:
    def __init__(self):
        self.templates: Dict[str, FingerprintTemplate] = {}
        self.scan_log: List[Dict[str, Any]] = []

    def enroll(self, user_id: str, finger_id: int, template_data: str = "", quality: float = 0.0) -> FingerprintTemplate:
        template_id = hashlib.sha256(f"{user_id}{finger_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        template = FingerprintTemplate(template_id=template_id, user_id=user_id, finger_id=finger_id, template_data=template_data, quality=quality)
        self.templates[template_id] = template
        return template

    def verify(self, user_id: str, finger_id: int, probe_data: str = "") -> bool:
        for t in self.templates.values():
            if t.user_id == user_id and t.finger_id == finger_id and t.active:
                if not probe_data or t.template_data == hashlib.sha256(probe_data.encode()).hexdigest():
                    self.scan_log.append({"user_id": user_id, "finger_id": finger_id, "match": True, "timestamp": datetime.now().isoformat()})
                    return True
        self.scan_log.append({"user_id": user_id, "finger_id": finger_id, "match": False, "timestamp": datetime.now().isoformat()})
        return False

    def get_user_templates(self, user_id: str) -> List[FingerprintTemplate]:
        return [t for t in self.templates.values() if t.user_id == user_id and t.active]

    def remove(self, template_id: str) -> bool:
        if template_id in self.templates:
            self.templates[template_id].active = False
            return True
        return False

    def count(self) -> int:
        return len([t for t in self.templates.values() if t.active])
