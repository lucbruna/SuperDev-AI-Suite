from __future__ import annotations

import logging
from typing import Any


class GatewaySecurity:
    """Gateway-level security: authentication of inbound requests and API key checks."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.gateway.security")
        self._valid_keys: dict[str, str] = {}  # api_key -> owner

    def register_key(self, api_key: str, owner: str = "anonymous") -> None:
        self._valid_keys[api_key] = owner

    def revoke_key(self, api_key: str) -> bool:
        return self._valid_keys.pop(api_key, None) is not None

    def authenticate(self, headers: dict[str, str]) -> tuple[bool, str]:
        """Validates an Authorization header (Bearer token or X-Api-Key)."""
        token = ""
        for key, value in headers.items():
            if key.lower() == "authorization":
                parts = value.split(" ", 1)
                if len(parts) == 2 and parts[0].lower() == "bearer":
                    token = parts[1]
            elif key.lower() in ("x-api-key", "api-key"):
                token = value
        if not token:
            return False, "missing credentials"
        owner = self._valid_keys.get(token)
        if owner is None:
            return False, "invalid credentials"
        return True, owner

    def enforce(self, headers: dict[str, str], required: bool = True) -> str | None:
        """Returns the authenticated owner, or raises PermissionError."""
        if not required:
            return None
        ok, owner = self.authenticate(headers)
        if not ok:
            raise PermissionError(owner)
        return owner
