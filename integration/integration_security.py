from __future__ import annotations

import html
import logging
import re
from typing import Any

_SECRET_PATTERN = re.compile(r"(api[_-]?key|secret|password|token|credential)", re.IGNORECASE)


class IntegrationSecurity:
    """Enforces access control, secret redaction, and input sanitization for integrations."""

    def __init__(self, enable_auth: bool = True) -> None:
        self._log = logging.getLogger("superdev.integration.security")
        self._enable_auth = enable_auth
        self._roles: dict[str, set[str]] = {"admin": {"*"}}
        self._api_keys: dict[str, str] = {}  # api_key -> owner

    # --- Sanitization -----------------------------------------------------

    def sanitize(self, value: str) -> str:
        return html.escape(value, quote=True)

    def sanitize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        return {str(k): html.escape(str(v), quote=True) for k, v in metadata.items()}

    def redact(self, value: Any, key: str = "") -> Any:
        """Redacts a single secret-like value."""
        if isinstance(value, str) and (_SECRET_PATTERN.search(key) or len(value) >= 12):
            return "***"
        return value

    def redact_config(self, config: dict[str, Any]) -> dict[str, Any]:
        """Returns a copy of the config with secret-looking values redacted."""
        return {str(k): self.redact(v, str(k)) for k, v in config.items()}

    # --- Access control ----------------------------------------------------

    def grant(self, user: str, role: str) -> None:
        self._roles.setdefault(user, set()).add(role)

    def check_permission(self, user: str, permission: str) -> bool:
        if not self._enable_auth:
            return True
        roles = self._roles.get(user, set())
        return "*" in roles or permission in roles

    def enforce(self, user: str, permission: str) -> None:
        if not self.check_permission(user, permission):
            raise PermissionError(f"user {user!r} lacks permission {permission!r}")

    # --- API keys ----------------------------------------------------------

    def issue_api_key(self, owner: str) -> str:
        import secrets

        key = f"sk-{secrets.token_hex(16)}"
        self._api_keys[key] = owner
        return key

    def validate_api_key(self, api_key: str) -> str | None:
        return self._api_keys.get(api_key)

    def revoke_api_key(self, api_key: str) -> bool:
        return self._api_keys.pop(api_key, None) is not None
