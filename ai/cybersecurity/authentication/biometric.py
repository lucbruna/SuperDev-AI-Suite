"""
Biometric Authentication
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class BiometricType(Enum):
    FINGERPRINT = "fingerprint"
    FACE = "face"
    IRIS = "iris"
    VOICE = "voice"
    PALM = "palm"


@dataclass
class BiometricTemplate:
    user_id: str
    biometric_type: BiometricType
    template_data: str = ""
    quality: float = 0.0
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class BiometricManager:
    def __init__(self):
        self.templates: Dict[str, List[BiometricTemplate]] = {}
        
    def register_template(self, user_id: str, biometric_type: BiometricType, template_data: str) -> BiometricTemplate:
        template = BiometricTemplate(
            user_id=user_id,
            biometric_type=biometric_type,
            template_data=template_data
        )
        if user_id not in self.templates:
            self.templates[user_id] = []
        self.templates[user_id].append(template)
        return template
        
    def verify(self, user_id: str, biometric_type: BiometricType, probe_data: str) -> bool:
        user_templates = self.templates.get(user_id, [])
        for template in user_templates:
            if template.biometric_type == biometric_type and template.is_active:
                if template.template_data == probe_data:
                    return True
        return False
        
    def get_user_templates(self, user_id: str) -> List[BiometricTemplate]:
        return self.templates.get(user_id, [])
        
    def revoke_template(self, user_id: str, biometric_type: BiometricType) -> bool:
        templates = self.templates.get(user_id, [])
        for t in templates:
            if t.biometric_type == biometric_type:
                t.is_active = False
                return True
        return False
        
    def revoke_all(self, user_id: str) -> int:
        templates = self.templates.get(user_id, [])
        count = 0
        for t in templates:
            if t.is_active:
                t.is_active = False
                count += 1
        return count
