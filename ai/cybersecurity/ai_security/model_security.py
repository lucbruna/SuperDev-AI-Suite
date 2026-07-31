"""
AI Model Security
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import secrets


class ThreatType(Enum):
    MODEL_THEFT = "model_theft"
    ADVERSARIAL_INPUT = "adversarial_input"
    MODEL_POISONING = "model_poisoning"
    INFERENCE_ATTACK = "inference_attack"
    MODEL_INVERSION = "model_inversion"


@dataclass
class ModelIntegrityCheck:
    model_id: str
    expected_hash: str
    actual_hash: str = ""
    verified: bool = False
    verified_at: Optional[datetime] = None


@dataclass
class AdversarialDetection:
    input_id: str
    is_adversarial: bool
    confidence: float = 0.0
    perturbation_magnitude: float = 0.0
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class ModelWatermark:
    model_id: str
    watermark_data: str
    owner: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class ModelSecurity:
    def __init__(self):
        self.integrity_checks: Dict[str, ModelIntegrityCheck] = {}
        self.watermarks: Dict[str, ModelWatermark] = {}
        self.threat_log: List[Dict[str, Any]] = []

    def register_model(self, model_id: str, model_hash: str) -> ModelIntegrityCheck:
        check = ModelIntegrityCheck(model_id=model_id, expected_hash=model_hash)
        self.integrity_checks[model_id] = check
        return check

    def verify_integrity(self, model_id: str, current_hash: str) -> bool:
        check = self.integrity_checks.get(model_id)
        if not check:
            return False
        check.actual_hash = current_hash
        check.verified = check.expected_hash == current_hash
        check.verified_at = datetime.now()
        return check.verified

    def add_watermark(self, model_id: str, watermark_data: str, owner: str = "") -> ModelWatermark:
        wm = ModelWatermark(model_id=model_id, watermark_data=watermark_data, owner=owner)
        self.watermarks[model_id] = wm
        return wm

    def detect_adversarial(self, input_id: str, input_data: str, expected_output: str, actual_output: str) -> AdversarialDetection:
        is_adv = expected_output != actual_output
        confidence = 0.9 if is_adv else 0.1
        detection = AdversarialDetection(input_id=input_id, is_adversarial=is_adv, confidence=confidence)
        if is_adv:
            self.threat_log.append({"type": ThreatType.ADVERSARIAL_INPUT.value, "input_id": input_id, "time": datetime.now().isoformat()})
        return detection

    def log_threat(self, threat_type: ThreatType, details: Dict[str, Any]) -> None:
        self.threat_log.append({"type": threat_type.value, "details": details, "time": datetime.now().isoformat()})

    def get_threats(self, threat_type: ThreatType = None) -> List[Dict[str, Any]]:
        if threat_type:
            return [t for t in self.threat_log if t["type"] == threat_type.value]
        return self.threat_log

    def get_integrity_status(self, model_id: str) -> Optional[ModelIntegrityCheck]:
        return self.integrity_checks.get(model_id)

    def count(self) -> int:
        return len(self.integrity_checks)
