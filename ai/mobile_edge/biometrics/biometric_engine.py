"""Biometric Engine - Core biometric authentication."""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class BiometricType(Enum):
    FINGERPRINT = "fingerprint"
    FACE = "face"
    VOICE = "voice"
    IRIS = "iris"
    BEHAVIORAL = "behavioral"


class AuthResult(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NOT_ENROLLED = "not_enrolled"
    HARDWARE_ERROR = "hardware_error"
    TIMEOUT = "timeout"


@dataclass
class BiometricEnrollment:
    enrollment_id: str
    user_id: str
    biometric_type: BiometricType
    template_hash: str = ""
    quality_score: float = 0.0
    enrolled_at: datetime = field(default_factory=datetime.now)
    active: bool = True


@dataclass
class AuthAttempt:
    attempt_id: str
    user_id: str
    biometric_type: BiometricType
    result: AuthResult = AuthResult.FAILURE
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class BiometricEngine:
    def __init__(self):
        self.enrollments: dict[str, list[BiometricEnrollment]] = {}
        self.attempts: list[AuthAttempt] = []

    def enroll(self, user_id: str, biometric_type: BiometricType, template_data: str = "", quality_score: float = 0.0) -> BiometricEnrollment:
        enrollment_id = hashlib.sha256(f"{user_id}{biometric_type.value}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        template_hash = hashlib.sha256(template_data.encode()).hexdigest() if template_data else ""
        enrollment = BiometricEnrollment(enrollment_id=enrollment_id, user_id=user_id, biometric_type=biometric_type, template_hash=template_hash, quality_score=quality_score)
        self.enrollments.setdefault(user_id, []).append(enrollment)
        return enrollment

    def authenticate(self, user_id: str, biometric_type: BiometricType, probe_data: str = "", confidence_threshold: float = 0.8) -> AuthResult:
        attempt_id = hashlib.sha256(f"{user_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        user_enrollments = self.enrollments.get(user_id, [])
        active = [e for e in user_enrollments if e.biometric_type == biometric_type and e.active]
        if not active:
            result = AuthResult.NOT_ENROLLED
            confidence = 0.0
        else:
            probe_hash = hashlib.sha256(probe_data.encode()).hexdigest() if probe_data else ""
            match = any(e.template_hash == probe_hash for e in active)
            if match or not probe_data:
                result = AuthResult.SUCCESS
                confidence = 0.95
            else:
                result = AuthResult.FAILURE
                confidence = 0.3
        attempt = AuthAttempt(attempt_id=attempt_id, user_id=user_id, biometric_type=biometric_type, result=result, confidence=confidence)
        self.attempts.append(attempt)
        return result

    def is_enrolled(self, user_id: str, biometric_type: BiometricType = None) -> bool:
        user_enrollments = self.enrollments.get(user_id, [])
        if biometric_type:
            return any(e.biometric_type == biometric_type and e.active for e in user_enrollments)
        return len(user_enrollments) > 0

    def revoke(self, enrollment_id: str) -> bool:
        for enrollments in self.enrollments.values():
            for e in enrollments:
                if e.enrollment_id == enrollment_id:
                    e.active = False
                    return True
        return False

    def get_enrollments(self, user_id: str) -> list[BiometricEnrollment]:
        return self.enrollments.get(user_id, [])

    def get_attempts(self, user_id: str = None, limit: int = 100) -> list[AuthAttempt]:
        attempts = self.attempts
        if user_id:
            attempts = [a for a in attempts if a.user_id == user_id]
        return attempts[-limit:]

    def count_enrollments(self) -> int:
        return sum(len(e) for e in self.enrollments.values())
