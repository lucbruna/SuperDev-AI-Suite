"""Cybersecurity Engine Interfaces — Protocol interfaces for security operations."""
from abc import ABC, abstractmethod
from typing import Any

from .security_models import Incident, SecurityUser, Threat, Vulnerability


class ThreatDetectionInterface(ABC):
    @abstractmethod
    def detect(self, data: dict[str, Any]) -> Threat | None:
        pass

    @abstractmethod
    def get_threats(self, severity: str | None = None) -> list[Threat]:
        pass


class VulnerabilityInterface(ABC):
    @abstractmethod
    def scan(self, target: str) -> list[Vulnerability]:
        pass

    @abstractmethod
    def get_vulnerabilities(self, severity: str | None = None) -> list[Vulnerability]:
        pass


class IncidentResponseInterface(ABC):
    @abstractmethod
    def respond(self, incident: Incident) -> Incident:
        pass

    @abstractmethod
    def get_incidents(self, status: str | None = None) -> list[Incident]:
        pass


class IdentityInterface(ABC):
    @abstractmethod
    def authenticate(self, username: str, password: str) -> SecurityUser | None:
        pass

    @abstractmethod
    def authorize(self, user_id: str, resource: str, action: str) -> bool:
        pass


class EncryptionInterface(ABC):
    @abstractmethod
    def encrypt(self, key_id: str, data: str) -> str:
        pass

    @abstractmethod
    def decrypt(self, key_id: str, encrypted_data: str) -> str:
        pass


class MonitoringInterface(ABC):
    @abstractmethod
    def monitor(self, event: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_alerts(self, severity: str | None = None) -> list[dict[str, Any]]:
        pass
