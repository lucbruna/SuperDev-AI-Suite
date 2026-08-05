"""Security Connector — facade over the security bridges."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.security.audit_bridge import get_audit_bridge
from modules.ai_video_studio.integration.security.authentication_bridge import (
    get_authentication_bridge,
)
from modules.ai_video_studio.integration.security.encryption_bridge import (
    get_encryption_bridge,
)
from modules.ai_video_studio.integration.security.permission_bridge import (
    get_permission_bridge,
)


class SecurityConnector(DomainConnector):
    """Permission, audit, encryption and authentication operations."""

    domain = "security"
    description = "Permission checks, audit trail, encryption and authentication bridges"

    def __init__(self) -> None:
        super().__init__()
        self._register("check_permission", self._permission)
        self._register("audit", self._audit)
        self._register("encrypt", self._encrypt)
        self._register("decrypt", self._decrypt)

    def _permission(self, data: dict[str, Any]) -> dict[str, Any]:
        missing = self._require(data, "role", "capability", action="check_permission")
        return missing or get_permission_bridge().check(data["role"], data["capability"])

    def _audit(self, data: dict[str, Any]) -> dict[str, Any]:
        missing = self._require(data, "actor", "action", action="audit")
        return missing or get_audit_bridge().record(data["actor"], data["action"],
                                                    target=data.get("target", ""),
                                                    result=data.get("result", "ok"),
                                                    detail=data.get("detail"))

    def _encrypt(self, data: dict[str, Any]) -> dict[str, Any]:
        missing = self._require(data, "plaintext", action="encrypt")
        return missing or get_encryption_bridge().encrypt(data["plaintext"])

    def _decrypt(self, data: dict[str, Any]) -> dict[str, Any]:
        missing = self._require(data, "token", action="decrypt")
        return missing or get_encryption_bridge().decrypt(data["token"], cipher=data.get("cipher", "fernet"))

    async def verify_token(self, token: str | None) -> dict[str, Any]:
        """Async convenience for the authentication bridge."""
        return await get_authentication_bridge().verify_token(token)


_security_connector: SecurityConnector | None = None


def get_security_connector() -> SecurityConnector:
    global _security_connector
    if _security_connector is None:
        _security_connector = SecurityConnector()
    return _security_connector
