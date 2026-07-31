from __future__ import annotations

import logging
from typing import Any


class CertificateManager:
    """Manages TLS/client certificates for outbound integration connections."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.auth.certificates")
        self._certificates: dict[str, dict[str, Any]] = {}

    def register(self, name: str, certificate: str, key: str = "",
                 expires_at: str = "") -> None:
        self._certificates[name] = {
            "certificate": certificate,
            "key": key,
            "expires_at": expires_at,
        }

    def get(self, name: str) -> dict[str, Any] | None:
        cert = self._certificates.get(name)
        return dict(cert) if cert else None

    def has(self, name: str) -> bool:
        return name in self._certificates

    def remove(self, name: str) -> bool:
        return self._certificates.pop(name, None) is not None

    def rotate(self, name: str, certificate: str, key: str = "") -> bool:
        if name not in self._certificates:
            return False
        self._certificates[name]["certificate"] = certificate
        if key:
            self._certificates[name]["key"] = key
        return True

    def list_names(self) -> list[str]:
        return sorted(self._certificates)
