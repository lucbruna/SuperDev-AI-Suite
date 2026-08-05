"""AIOS Services — platform service layer.

Authentication (tokens), authorization (RBAC), audit trail,
notifications, storage, cache, configuration, structured logging and
metrics. All services are deterministic and in-memory by default.
"""

from __future__ import annotations

from .audit import AuditService
from .authentication import AuthenticationService
from .authorization import ROLE_ADMIN, ROLE_AGENT, ROLE_OPERATOR, ROLE_VIEWER, AuthorizationService
from .cache import CacheService
from .configuration import ConfigurationService
from .logging import LEVELS, LoggingService
from .metrics import MetricsService
from .notifications import NotificationService
from .storage import StorageService

__all__ = [
    "AuthenticationService",
    "AuthorizationService",
    "AuditService",
    "NotificationService",
    "StorageService",
    "CacheService",
    "ConfigurationService",
    "LoggingService",
    "MetricsService",
    "ROLE_ADMIN",
    "ROLE_OPERATOR",
    "ROLE_AGENT",
    "ROLE_VIEWER",
    "LEVELS",
]
