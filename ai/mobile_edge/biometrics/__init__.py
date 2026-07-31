"""Biometrics subsystem for Mobile & Edge AI Engine."""

from .biometric_engine import AuthAttempt, AuthResult, BiometricEngine, BiometricEnrollment, BiometricType
from .face import FaceRecognitionManager, FaceTemplate
from .fingerprint import FingerprintManager, FingerprintTemplate
from .voice import Voiceprint, VoiceRecognitionManager

__all__ = [
    "BiometricEngine",
    "BiometricType",
    "AuthResult",
    "BiometricEnrollment",
    "AuthAttempt",
    "FingerprintManager",
    "FingerprintTemplate",
    "FaceRecognitionManager",
    "FaceTemplate",
    "VoiceRecognitionManager",
    "Voiceprint",
]
