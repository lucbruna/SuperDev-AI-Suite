"""Vault subsystem (Volume 16) — secret storage with TTL, versions, rotation."""

from __future__ import annotations

import time
from typing import Any

from ..security_models import VaultSecret


class VaultEngine:
    """In-memory secret vault with TTL, versioning and rotation reminders."""

    name = "vault"
    description = "Secret storage with TTL, versioning and rotation"

    def __init__(self, engine: Any | None = None, default_ttl_hours: float = 24.0) -> None:
        self.engine = engine
        self.default_ttl_hours = default_ttl_hours
        self._secrets: dict[str, VaultSecret] = {}

    def store(
        self,
        name: str,
        value: str,
        ttl_hours: float | None = None,
        owner: str = "system",
    ) -> VaultSecret:
        """Store (or overwrite) a secret, incrementing its version."""
        now = time.time()
        previous = self._secrets.get(name)
        version = (previous.version + 1) if previous else 1
        ttl = ttl_hours if ttl_hours is not None else self.default_ttl_hours
        secret = VaultSecret(
            name=name,
            value=value,
            owner=owner,
            created_at=now,
            expires_at=now + max(0.0, ttl) * 3600,
            version=version,
            rotation_due=now + max(0.0, ttl) * 0.8 * 3600,
        )
        self._secrets[name] = secret
        if self.engine is not None:
            self.engine.metrics.increment("security.vault_writes")
            self.engine.registry.register_secret(name, secret)
        return secret

    def get(self, name: str) -> str | None:
        """Return the raw secret value (None when missing or expired)."""
        secret = self._secrets.get(name)
        if secret is None or secret.is_expired():
            if self.engine is not None:
                self.engine.metrics.increment(
                    "security.vault_reads", labels={"result": "miss"}
                )
            return None
        if self.engine is not None:
            self.engine.metrics.increment(
                "security.vault_reads", labels={"result": "hit"}
            )
        return secret.value

    def describe(self, name: str) -> VaultSecret | None:
        return self._secrets.get(name)

    def delete(self, name: str) -> bool:
        existed = name in self._secrets
        self._secrets.pop(name, None)
        if existed and self.engine is not None:
            self.engine.metrics.increment("security.vault_deletes")
        return existed

    def list_names(self) -> list[str]:
        return list(self._secrets.keys())

    def expired(self) -> list[str]:
        return [name for name, s in self._secrets.items() if s.is_expired()]

    def due_for_rotation(self, hours: float = 1.0) -> list[str]:
        horizon = time.time() + max(0.0, hours) * 3600
        return [
            name
            for name, s in self._secrets.items()
            if s.rotation_due is not None and s.rotation_due <= horizon
        ]

    def rotate(self, name: str, new_value: str) -> VaultSecret | None:
        """Rotate a secret, keeping the same name with a new version."""
        current = self._secrets.get(name)
        if current is None:
            return None
        return self.store(
            name, new_value, ttl_hours=(current.expires_at - current.created_at) / 3600,
            owner=current.owner,
        )

    def status(self) -> dict[str, Any]:
        return {
            "secrets": len(self._secrets),
            "expired": len(self.expired()),
            "due_for_rotation": len(self.due_for_rotation()),
        }


__all__ = ["VaultEngine"]
