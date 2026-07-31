"""Security interfaces and abstract base classes."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AuthProvider(ABC):
    @abstractmethod
    def authenticate(self, credentials: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def validate_token(self, token: str) -> bool: ...

    @abstractmethod
    def revoke_token(self, token: str) -> bool: ...


class EncryptionProvider(ABC):
    @abstractmethod
    def encrypt(self, data: str, key_id: str = "") -> str: ...

    @abstractmethod
    def decrypt(self, ciphertext: str, key_id: str = "") -> str: ...

    @abstractmethod
    def rotate_keys(self) -> bool: ...


class AuditProvider(ABC):
    @abstractmethod
    def log(self, entry: dict[str, Any]) -> None: ...

    @abstractmethod
    def query(self, filters: dict[str, Any]) -> list[dict[str, Any]]: ...


class ThreatDetector(ABC):
    @abstractmethod
    def analyze(self, event: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def get_threat_level(self) -> str: ...


class PolicyEngine(ABC):
    @abstractmethod
    def evaluate(self, request: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    def enforce(self, policy_id: str, context: dict[str, Any]) -> bool: ...


class ComplianceChecker(ABC):
    @abstractmethod
    def check_compliance(self, standard: str) -> dict[str, Any]: ...

    @abstractmethod
    def generate_report(self, standard: str) -> dict[str, Any]: ...
