"""License validation."""
from __future__ import annotations

import time
from typing import Any


class LicenseValidator:
    def __init__(self) -> None:
        self._rules: dict[str, Any] = {}
    def set_rules(self, license_id: str, max_activations: int = 1, expires_at: float = 0, allowed_plans: list = None) -> None:
        self._rules[license_id] = {"max_activations": max_activations, "expires_at": expires_at, "allowed_plans": allowed_plans or []}
    def validate(self, license: dict[str, Any], current_activations: int) -> dict[str, Any]:
        errors = []
        rules = self._rules.get(license.get("id", ""), {})
        if license.get("status") != "active":
            errors.append("license_not_active")
        if rules.get("expires_at") and time.time() > rules["expires_at"]:
            errors.append("license_expired")
        if current_activations >= rules.get("max_activations", 1):
            errors.append("max_activations_reached")
        if rules.get("allowed_plans") and license.get("plan_id") not in rules["allowed_plans"]:
            errors.append("plan_not_allowed")
        return {"valid": len(errors) == 0, "errors": errors}
    def list_rules(self) -> dict[str, Any]:
        return dict(self._rules)
    def remove_rules(self, license_id: str) -> bool:
        if license_id in self._rules:
            del self._rules[license_id]
            return True
        return False
