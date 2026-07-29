"""
Security Manager - Enterprise security, encryption, and threat detection
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from enterprise_ai_core.config import SecurityConfig
from enterprise_ai_core.models import SecurityContext, Severity, Event, EventType
from enterprise_ai_core.security.encryption_manager import EncryptionManager
from enterprise_ai_core.security.identity_manager import IdentityManager
from enterprise_ai_core.security.threat_detection import ThreatDetector
from enterprise_ai_core.security.access_policy import AccessPolicyManager


class SecurityManager:
    """Enterprise security management"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config.security
        self.encryption = EncryptionManager(self.config)
        self.identity = IdentityManager(self.config)
        self.threat_detector = ThreatDetector(self.config)
        self.access_policy = AccessPolicyManager(self.config)
        self._initialized = False

    async def initialize(self) -> None:
        await self.encryption.initialize()
        await self.identity.initialize()
        await self.threat_detector.initialize()
        await self.access_policy.initialize()
        self._initialized = True

    async def shutdown(self) -> None:
        await self.encryption.shutdown()
        await self.identity.shutdown()
        await self.threat_detector.shutdown()
        await self.access_policy.shutdown()

    async def authenticate(
        self,
        credentials: Dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[SecurityContext]:
        context = await self.identity.authenticate(credentials, ip_address, user_agent)
        if context:
            await self._log_security_event("authentication", "success", context)
        else:
            await self._log_security_event("authentication", "failure", None, Severity.WARNING, {"ip": ip_address})
        return context

    async def authorize(
        self,
        context: SecurityContext,
        resource: str,
        action: str,
        resource_id: Optional[str] = None,
    ) -> bool:
        allowed = await self.access_policy.check_permission(context, resource, action, resource_id)

        await self._log_security_event(
            "authorization",
            "success" if allowed else "denied",
            context,
            Severity.INFO if allowed else Severity.WARNING,
            {"resource": resource, "action": action, "resource_id": resource_id},
        )

        if not allowed:
            await self.threat_detector.analyze_failed_access(context, resource, action)

        return allowed

    async def encrypt(self, data: str, context: Optional[SecurityContext] = None) -> str:
        return await self.encryption.encrypt(data, context)

    async def decrypt(self, encrypted_data: str, context: Optional[SecurityContext] = None) -> str:
        return await self.encryption.decrypt(encrypted_data, context)

    async def hash_password(self, password: str) -> str:
        return await self.encryption.hash_password(password)

    async def verify_password(self, password: str, hashed: str) -> bool:
        return await self.encryption.verify_password(password, hashed)

    async def generate_token(self, context: SecurityContext, expires_in: int = 3600) -> str:
        return await self.identity.generate_token(context, expires_in)

    async def validate_token(self, token: str) -> Optional[SecurityContext]:
        return await self.identity.validate_token(token)

    async def revoke_token(self, token: str) -> bool:
        return await self.identity.revoke_token(token)

    async def check_rate_limit(self, identifier: str, limit: int = 100, window: int = 60) -> bool:
        return await self.threat_detector.check_rate_limit(identifier, limit, window)

    async def scan_for_threats(self, data: Dict[str, Any], context: SecurityContext) -> List[Dict]:
        return await self.threat_detector.scan(data, context)

    async def get_security_context(self, token: str) -> Optional[SecurityContext]:
        return await self.identity.validate_token(token)

    async def _log_security_event(
        self,
        action: str,
        outcome: str,
        context: Optional[SecurityContext],
        severity: Severity = Severity.INFO,
        details: Optional[Dict] = None,
    ) -> None:
        await self.orchestrator.audit_manager.log(
            event_type=f"security.{action}",
            action=action,
            actor_id=context.user_id if context else None,
            actor_type="user" if context and context.user_id else "system",
            outcome=outcome,
            details=details or {},
            severity=severity,
            ip_address=context.ip_address if context else None,
            user_agent=context.user_agent if context else None,
        )

    async def rotate_keys(self) -> None:
        await self.encryption.rotate_keys()
        await self.identity.rotate_secrets()

    def get_stats(self) -> Dict[str, Any]:
        return {
            "encryption": self.encryption.get_stats(),
            "identity": self.identity.get_stats(),
            "threats": self.threat_detector.get_stats(),
            "access_policy": self.access_policy.get_stats(),
        }