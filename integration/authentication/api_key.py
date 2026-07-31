from __future__ import annotations

import logging
import secrets
from typing import Any


class APIKeyProvider:
    """API key issuance, validation, and revocation."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.auth.api_key")
        self._keys: dict[str, str] = {}  # key -> owner

    def issue(self, owner: str, prefix: str = "sk") -> str:
        key = f"{prefix}-{secrets.token_hex(16)}"
        self._keys[key] = owner
        return key

    def validate(self, api_key: str) -> str | None:
        """Returns the owner when the key is valid, else None."""
        return self._keys.get(api_key)

    def revoke(self, api_key: str) -> bool:
        return self._keys.pop(api_key, None) is not None

    def list_keys(self) -> list[str]:
        return list(self._keys)

    def snapshot(self) -> dict[str, int]:
        return {"keys": len(self._keys)}
