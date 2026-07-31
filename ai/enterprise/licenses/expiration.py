"""License expiration."""
from __future__ import annotations

import time
from typing import Any


class LicenseExpiration:
    def __init__(self) -> None:
        self._expirations: dict[str, float] = {}
        self._warnings: dict[str, list[dict[str, Any]]] = {}
    def set_expiration(self, license_id: str, expires_at: float) -> None:
        self._expirations[license_id] = expires_at
    def get_expiration(self, license_id: str) -> float:
        return self._expirations.get(license_id, 0.0)
    def is_expired(self, license_id: str) -> bool:
        exp = self._expirations.get(license_id)
        return exp is not None and time.time() > exp
    def days_until_expiration(self, license_id: str) -> float:
        exp = self._expirations.get(license_id, 0)
        if exp == 0:
            return float('inf')
        return max(0, (exp - time.time()) / 86400)
    def add_warning(self, license_id: str, days_before: int, message: str) -> None:
        self._warnings.setdefault(license_id, []).append({"days_before": days_before, "message": message})
    def get_warnings(self, license_id: str) -> list[dict[str, Any]]:
        return self._warnings.get(license_id, [])
    def get_expiring_soon(self, days: int = 30) -> list[str]:
        cutoff = time.time() + days * 86400
        return [lid for lid, exp in self._expirations.items() if 0 < exp <= cutoff]
    def list_all(self) -> dict[str, float]:
        return dict(self._expirations)
