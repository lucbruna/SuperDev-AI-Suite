"""
Adversarial Attack Defense
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import math
import hashlib


class AttackType(Enum):
    FGSM = "fgsm"
    PGD = "pgd"
    CW = "cw"
    DEEPFOOL = "deepfool"
    JSMA = "jsma"
    PATCH = "patch"


@dataclass
class AdversarialInput:
    input_id: str
    original_hash: str
    perturbed_hash: str
    perturbation_magnitude: float = 0.0
    attack_type: AttackType = AttackType.FGSM
    detected: bool = False


@dataclass
class DefenseResult:
    input_id: str
    defended: bool
    method: str = ""
    confidence: float = 0.0
    original_prediction: Any = None
    defended_prediction: Any = None


class AdversarialDefense:
    def __init__(self):
        self.detected_inputs: List[AdversarialInput] = []
        self.defense_methods: List[str] = ["input_validation", "feature_squeezing", "randomized_smoothing", "adversarial_training"]
        self.active_method: str = "input_validation"
        self.perturbation_threshold: float = 0.1

    def detect_perturbation(self, input_id: str, original: str, perturbed: str) -> AdversarialInput:
        orig_hash = hashlib.sha256(original.encode()).hexdigest()
        pert_hash = hashlib.sha256(perturbed.encode()).hexdigest()
        mag = self._calculate_magnitude(original, perturbed)
        detected = mag > self.perturbation_threshold
        result = AdversarialInput(input_id=input_id, original_hash=orig_hash, perturbed_hash=pert_hash, perturbation_magnitude=mag, detected=detected)
        self.detected_inputs.append(result)
        return result

    def _calculate_magnitude(self, original: str, perturbed: str) -> float:
        if original == perturbed:
            return 0.0
        max_len = max(len(original), len(perturbed))
        diff_count = sum(1 for a, b in zip(original, perturbed) if a != b) + abs(len(original) - len(perturbed))
        return diff_count / max_len

    def defend(self, input_id: str, input_data: str) -> DefenseResult:
        result = DefenseResult(input_id=input_id, defended=True, method=self.active_method, confidence=0.85)
        return result

    def set_method(self, method: str) -> bool:
        if method in self.defense_methods:
            self.active_method = method
            return True
        return False

    def get_detected(self) -> List[AdversarialInput]:
        return [i for i in self.detected_inputs if i.detected]

    def set_threshold(self, threshold: float) -> None:
        self.perturbation_threshold = threshold

    def get_stats(self) -> Dict[str, int]:
        total = len(self.detected_inputs)
        detected = sum(1 for i in self.detected_inputs if i.detected)
        return {"total": total, "detected": detected, "clean": total - detected}

    def count(self) -> int:
        return len(self.detected_inputs)
