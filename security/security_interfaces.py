"""Interfaces / ABCs for the Security Engine (Volume 16)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .base import SecurityReport


class ISecurityAnalyzer(ABC):
    """Contract for any security analyzer (OWASP, SBOM, secrets, ...)."""

    name: str = "analyzer"
    description: str = ""

    @abstractmethod
    async def analyze(self, target: str) -> SecurityReport:
        """Run the analysis against a target and return a report."""
        raise NotImplementedError


class ICryptoProvider(ABC):
    """Contract for crypto operations (encrypt/decrypt/hash/sign)."""

    @abstractmethod
    def encrypt(self, plaintext: str, key: bytes) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, payload: dict[str, Any], key: bytes) -> str:
        raise NotImplementedError


class ISecretStore(ABC):
    """Contract for a secret store (vault)."""

    @abstractmethod
    def get(self, name: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def set(self, name: str, value: str, **kwargs: Any) -> bool:
        raise NotImplementedError
