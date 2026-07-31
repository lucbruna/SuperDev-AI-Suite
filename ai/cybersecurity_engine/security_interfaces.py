"""Cybersecurity Engine Interfaces — Protocol interfaces for security operations."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .security_models import Threat, Vulnerability, Incident, SecurityUser


class ThreatDetectionInterface(ABC):
    @abstractmethod
    def detect(self, data: Dict[str, Any]) -> Optional[Threat]:
        pass

    @abstractmethod
    def get_threats(self, severity: Optional[str] = None) -> List[Threat]:
        pass


class VulnerabilityInterface(ABC):
    @abstractmethod
    def scan(self, target: str) -> List[Vulnerability]:
        pass

    @abstractmethod
    def get_vulnerabilities(self, severity: Optional[str] = None) -> List[Vulnerability]:
        pass


class IncidentResponseInterface(ABC):
    @abstractmethod
    def respond(self, incident: Incident) -> Incident:
        pass

    @abstractmethod
    def get_incidents(self, status: Optional[str] = None) -> List[Incident]:
        pass


class IdentityInterface(ABC):
    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[SecurityUser]:
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
    def monitor(self, event: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def get_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        pass
