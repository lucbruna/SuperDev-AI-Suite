"""Security — permission, audit, encryption and authentication bridges."""
from modules.ai_video_studio.integration.security.audit_bridge import (
    AuditBridge,
    get_audit_bridge,
)
from modules.ai_video_studio.integration.security.authentication_bridge import (
    AuthenticationBridge,
    get_authentication_bridge,
)
from modules.ai_video_studio.integration.security.encryption_bridge import (
    EncryptionBridge,
    get_encryption_bridge,
)
from modules.ai_video_studio.integration.security.permission_bridge import (
    PermissionBridge,
    get_permission_bridge,
)
from modules.ai_video_studio.integration.security.security_connector import (
    SecurityConnector,
    get_security_connector,
)

__all__ = [
    "AuditBridge",
    "get_audit_bridge",
    "AuthenticationBridge",
    "get_authentication_bridge",
    "EncryptionBridge",
    "get_encryption_bridge",
    "PermissionBridge",
    "get_permission_bridge",
    "SecurityConnector",
    "get_security_connector",
]
