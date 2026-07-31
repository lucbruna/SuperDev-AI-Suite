from __future__ import annotations

import logging
import secrets
from typing import Any


class SecretManager:
    """Stores and retrieves secrets (credentials, keys) with redaction."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.auth.secrets")
        self._secrets: dict[str, str] = {}

    def store(self, name: str, value: str) -> None:
        self._secrets[name] = value

    def get(self, name: str) -> str | None:
        return self._secrets.get(name)

    def delete(self, name: str) -> bool:
        return self._secrets.pop(name, None) is not None

    def exists(self, name: str) -> bool:
        return name in self._secrets

    def generate(self, name: str, length: int = 32) -> str:
        value = secrets.token_hex(length // 2 + 1)[:length]
        self._secrets[name] = value
        return value

    def list_names(self) -> list[str]:
        return sorted(self._secrets)

    def rotate(self, name: str) -> str | None:
        if name not in self._secrets:
            return None
        return self.generate(name)

    def snapshot(self) -> dict[str, int]:
        return {"secrets": len(self._secrets)}
